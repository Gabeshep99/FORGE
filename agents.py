"""Three logical agents; the Researcher uses two calls to separate search from extraction."""
import json, os, re
from urllib.parse import urlsplit
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, APITimeoutError
from pydantic import ValidationError
from schemas import Research, Opportunities, Roadmap, Critique, DIMENSIONS
import prompts
from cost_control import UsageLedger
from model_advisor import profile_caps, recommended_reasoning

class WorkflowError(Exception):
    """Safe, actionable message suitable for the user interface."""


def safe_url(url):
    parsed = urlsplit(str(url))
    return parsed.scheme in ('https','http') and bool(parsed.hostname) and not parsed.username


def cited_sources(raw):
    """Registry from actual response annotations, not URLs invented in generated prose."""
    registry = {}
    for output in raw.get('output', []):
        if output.get('type') != 'message': continue
        for content in output.get('content', []):
            for annotation in content.get('annotations', []):
                if annotation.get('type') == 'url_citation' and safe_url(annotation.get('url','')):
                    registry[annotation['url']] = annotation.get('title', annotation['url'])
    return registry


def validate_refs(obj, allowed):
    """Enforce reference membership in structured fields and inline text recursively."""
    data = obj.model_dump(mode='json') if hasattr(obj,'model_dump') else obj
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'evidence_ids' and not set(item).issubset(allowed):
                    raise WorkflowError('Output cited unapproved or unknown evidence. Retry the stage.')
                visit(item)
        elif isinstance(value, list):
            for item in value: visit(item)
        elif isinstance(value, str):
            for ref in re.findall(r'\[(E\d+)\]', value):
                if ref not in allowed: raise WorkflowError('Output contains an unapproved inline citation. Retry the stage.')
    visit(data)


def validate_opportunities(result, approved):
    validate_refs(result, {e.id for e in approved})
    ids = [o.id for o in result.opportunities]
    if len(set(ids)) != len(ids): raise WorkflowError('Duplicate opportunity IDs. Retry the stage.')
    for o in result.opportunities:
        if sorted(a.dimension for a in o.assessments) != sorted(DIMENSIONS):
            raise WorkflowError('Incomplete evaluation rubric. Retry the stage.')
        if any(a.rating != 'Unknown' and not a.evidence_ids for a in o.assessments):
            raise WorkflowError('A rating lacks supporting evidence. Retry the stage.')
    return result



def api_compatible_schema(value):
    """Remove unsupported URI format hints from API schemas."""
    if isinstance(value, dict):
        return {
            k: api_compatible_schema(v)
            for k, v in value.items()
            if not (k == "format" and v == "uri")
        }
    if isinstance(value, list):
        return [api_compatible_schema(v) for v in value]
    return value


class Agents:
    def __init__(self, log, model=None, client=None, models=None, ledger=None, profile="Balanced (recommended)"):
        self.log = log
        self.models = models or {}
        self.profile = profile
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-6.1-terra')
        self.ledger = ledger if ledger is not None else UsageLedger()
        if client is None:
            if not os.getenv('OPENAI_API_KEY'): raise WorkflowError('Add OPENAI_API_KEY to .env or deployment secrets, or choose the offline aviation demo.')
            client = OpenAI(timeout=180, max_retries=0)
        self.client = client

    def call(self, agent, instructions, data, schema=None, search=False):
        selected_model = self.models.get(agent.split('/')[0], self.model)
        output_caps = profile_caps(self.profile)
        output_cap = output_caps.get(agent, 8500)
        payload = json.dumps(data, ensure_ascii=False, default=str)
        try:
            reservation = self.ledger.preflight(
                selected_model, len(payload) + len(instructions), output_cap, search)
        except ValueError as exc:
            raise WorkflowError(str(exc)) from exc
        request = dict(model=selected_model, instructions=instructions,
                       input=payload, store=False, max_output_tokens=output_cap,
                       reasoning={'effort': recommended_reasoning(selected_model, self.profile)})
        if search:
            request.update(tools=[{'type':'web_search'}], tool_choice='required',
                           include=['web_search_call.action.sources'])
        if schema:
            # Request a strict JSON schema; validate after logging the raw response, including malformed output.
            request['text'] = {'format': {'type':'json_schema', 'name':schema.__name__, 'strict':True, 'schema':api_compatible_schema(schema.model_json_schema())}}
        call_id = self.log.write('api_request', agent=agent, model=selected_model,
            prompt_version=prompts.VERSION, user_input=data, developer_prompt=instructions,
            prompt_sent=request['input'], settings={k:v for k,v in request.items() if k not in ('instructions','input','text_format')},
            output_schema=schema.model_json_schema() if schema else None)['timestamp']
        try:
            result = self.client.responses.create(**request)
            raw = result.model_dump(mode='json')
            cost_row = self.ledger.record(selected_model, agent, result, search, reservation)
            self.log.write('api_usage', **cost_row)
            self.log.write('api_response', agent=agent, model=selected_model, call_id=call_id,
                           response=raw, sources=cited_sources(raw))
            if result.status != 'completed':
                reason = (raw.get('incomplete_details') or {}).get('reason','unknown')
                self.log.write('stage_incomplete', agent=agent, model=selected_model,
                               reason=reason, output_tokens=(raw.get('usage') or {}).get('output_tokens'),
                               max_output_tokens=output_cap)
                raise WorkflowError(f'{agent} was incomplete ({reason}). See the audit log; '
                                    'review output profile and estimated cost before retrying this stage.')
            if schema:
                if not result.output_text: raise WorkflowError('The model declined or returned no structured output. Revise the input and retry.')
                return schema.model_validate_json(result.output_text)
            return result
        except (RateLimitError, AuthenticationError, APITimeoutError, APIError, ValidationError, ValueError) as exc:
            self.log.write('api_error', agent=agent, model=selected_model, call_id=call_id, error_type=type(exc).__name__)
            if isinstance(exc, RateLimitError): message = 'Rate limit or quota reached. Check API billing/quota, then retry; completed stages are preserved.'
            elif isinstance(exc, AuthenticationError): message = 'API authentication failed. Check the key in your environment or deployment secrets.'
            elif isinstance(exc, APITimeoutError): message = 'The API timed out. Your previous stage is preserved; retry when ready.'
            elif isinstance(exc, (ValidationError, ValueError)): message = 'The model returned invalid structured data. Retry this stage.'
            else: message = 'The API request failed. Check network access, model access and web-search support, then retry.'
            if isinstance(exc, APIError):
                detail = getattr(exc, "body", None)
                if isinstance(detail, dict):
                    detail = detail.get("error", detail)
                if isinstance(detail, dict):
                    print("FORGE API ERROR:", {
                        "type": type(exc).__name__,
                        "status": getattr(exc, "status_code", None),
                        "code": detail.get("code"),
                        "param": detail.get("param"),
                        "message": detail.get("message")
                    })
                else:
                    print("FORGE API ERROR TYPE:", type(exc).__name__)
            raise WorkflowError(message) from exc

    def research(self, challenge):
        raw = self.call('Researcher/search', prompts.RESEARCH, challenge.model_dump(), search=True)
        registry = cited_sources(raw.model_dump(mode='json'))
        if not registry: raise WorkflowError('Research returned no traceable web citations. No evidence was approved. Refine the challenge and retry.')
        result = self.call('Researcher/extract', prompts.EXTRACT,
             {'challenge':challenge.model_dump(), 'narrative':raw.output_text, 'citation_registry':registry}, Research)
        # Compare normalized URLs to account for Pydantic's trailing slash on a host-only URL.
        allowed = {str(__import__('pydantic').HttpUrl(u)) for u in registry}
        if any(str(e.source_url) not in allowed for e in result.findings):
            raise WorkflowError('A finding used a source outside the web citation registry. Research was blocked; retry.')
        ids = [e.id for e in result.findings]
        if len(set(ids)) != len(ids) or any(not re.fullmatch(r'E\d+', i) for i in ids):
            raise WorkflowError('Invalid or duplicate evidence IDs. Retry research.')
        return result

    def opportunities(self, challenge, approved):
        if not approved: raise WorkflowError('Approve at least one evidence finding first.')
        result = self.call('Strategist/opportunities', prompts.STRATEGIST,
                          {'challenge':challenge.model_dump(), 'approved_evidence':[e.model_dump(mode='json') for e in approved]}, Opportunities)
        return validate_opportunities(result, approved)

    def roadmap(self, challenge, approved, selected, deep_id, feedback):
        if not selected or deep_id not in {o.id for o in selected}: raise WorkflowError('Select a deep-dive opportunity from your included opportunities.')
        result = self.call('Strategist/roadmap', prompts.ROADMAP,
            {'challenge':challenge.model_dump(), 'approved_evidence':[e.model_dump(mode='json') for e in approved],
             'selected_opportunities':[o.model_dump() for o in selected], 'deep_dive_id':deep_id, 'human_feedback':feedback}, Roadmap)
        validate_refs(result, {e.id for e in approved})
        if [p.name for p in result.phases] != ['Validation','Prototype','Pilot','Evaluation','Scale Decision']:
            raise WorkflowError('The roadmap omitted or reordered required phases. Retry this stage.')
        return result

    def critic(self, challenge, approved, selected, roadmap, feedback):
        result = self.call('Critic', prompts.CRITIC,
            {'challenge':challenge.model_dump(), 'approved_evidence':[e.model_dump(mode='json') for e in approved],
             'selected_opportunities':[o.model_dump() for o in selected], 'roadmap':roadmap.model_dump(), 'human_feedback':feedback}, Critique)
        validate_refs(result, {e.id for e in approved})
        if len(result.issues) != 13 or len({i.category for i in result.issues}) != 13:
            raise WorkflowError('Critic review did not cover all required categories. Retry the review.')
        return result
