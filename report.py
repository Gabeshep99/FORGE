"""Deterministic brief assembly: no new unsourced claims introduced by a final LLM call."""
import re
from datetime import datetime, timezone
from agents import WorkflowError
from methodology import rubric_markdown

def bullet(items): return '\n'.join('- '+str(x) for x in items)
def table_cell(value): return str(value).replace('|', '\\|').replace('\n',' ')

def build_report(s, session_id):
    if not s.critique or not s.roadmap: raise WorkflowError('Complete the roadmap and critic review before exporting the final brief.')
    r, c, ch = s.roadmap, s.critique, s.challenge
    deep = next(o for o in s.selected if o.id==s.deep_id)
    text = [f'# FORGE | Technology Strategy Brief\n\n**{ch.organization}** · {ch.industry} · {ch.horizon}',
      f'Created: {datetime.now(timezone.utc).isoformat()}\n\nSession: `{session_id}` · Mode: **{s.mode}**',
      '> Decision support only. Hypotheses, timing estimates and proposed KPIs are not achieved outcomes. '+('OFFLINE DEMO: curated evidence and template analysis, not live AI research.' if s.mode=='Demo' else 'AI-generated analysis based on human-approved evidence; verify source support before acting.'),
      '## 1. Executive Summary\n'+r.executive_summary,
      '## 2. Strategic Challenge\n'+ch.challenge+'\n\nContext: '+(ch.context or 'Not provided.'),
      '## 3. Current State\nThe challenge describes the user-provided situation. An independent organizational diagnosis has not been established.\n\nResearch coverage gaps:\n'+bullet(s.research.gaps),
      '## 4. Key Evidence']
    for e in s.approved:
        text.append(f'### {e.id} — {e.finding}\n{e.explanation}\n\nSource: [{e.source_title}]({e.source_url}) · Published: {e.publication_date or "Unknown"}\n\nEvidence strength: {e.strength}. {e.strength_reason}\n\nRelevance: {e.relevance}\n\nLimitation: {e.limitation}')
    text.append('## 5. Emerging Technology Opportunities\nMaturity is application-specific; commercial precedents are not automatically emerging technologies.')
    for o in s.opportunities.opportunities:
        status = 'Selected for consideration' if o.id in s.selected_ids else 'Not selected'
        text.append(f'### {o.id} — {o.name} ({status})\n**Problem:** {o.problem_addressed}\n\n**Technology:** {o.technology}\n\n**How it works:** {o.how_it_works}\n\n**Evidence:** '+', '.join(f'[{i}]' for i in o.evidence_ids)+f'\n\n**Value hypothesis:** {o.business_value_hypothesis}\n\n**Maturity:** {o.maturity}. {o.maturity_reason}\n\n**Competition:** {o.competitive_implications}\n\n**Barriers:** '+ '; '.join(o.barriers)+f'\n\n**Timing estimate:** {o.time_horizon_estimate}')
    text.append('## 6. Opportunity Evaluation\n'+rubric_markdown())
    for o in s.opportunities.opportunities:
        text.append(f'### {o.name}\n| Dimension | Assessment | Rationale / evidence |\n|---|---|---|\n'+'\n'.join(f'| {a.dimension} | {a.rating} | {table_cell(a.reason)} '+', '.join(f'[{i}]' for i in a.evidence_ids)+' |' for a in o.assessments))
    text.extend(['## 7. Selected Opportunity\n'+deep.name+'\n\n**Human priorities:** '+(s.feedback or 'None added.')+'\n\n**Response to feedback:** '+r.feedback_response,
      '## 8. Business-Value Hypothesis\n'+deep.business_value_hypothesis,
      '## 9. Human-Centered AI Considerations\n'+bullet(r.human_factors)+'\n\nStakeholders:\n'+bullet(r.stakeholders),
      '## 10. Risks and Assumptions\n'+bullet(r.assumptions)+'\n\nOpportunity barriers:\n'+bullet(deep.barriers),
      '## 11. Pilot Recommendation\n'+r.proposed_pilot+'\n\n**Objective:** '+r.strategic_objective+'\n\n**Rationale:** '+r.why_it_matters+'\n\nSupporting evidence: '+', '.join(f'[{i}]' for i in r.evidence_ids),
      '## 12. Implementation Roadmap\n**Required capabilities**\n'+bullet(r.required_capabilities)+'\n\n**Data requirements**\n'+bullet(r.data_requirements)+'\n\n**Technical requirements**\n'+bullet(r.technical_requirements)])
    for n,p in enumerate(r.phases,1):
        text.append(f'### Phase {n} — {p.name}\n{bullet(p.actions)}\n\nOwner: {p.owner}\n\nDuration: {p.duration_estimate}\n\nExit gate: {p.exit_gate}')
    text.append('## 13. KPIs\nThese are proposed measurement plans; no improvement is claimed.')
    for k in r.kpis: text.append(f'### {k.name}\n{k.definition}\n\nBaseline: {k.baseline_plan}\n\nMeasurement: {k.measurement_method}\n\nDecision rule: {k.decision_rule}')
    text.append(f'## 14. Independent Critic Review\n**{c.verdict}**\n\n{c.summary}\n\nIndependence means a separate prompted review, not independent institutional assurance.\n\nStrongest counterargument: {c.strongest_counterargument}\n\nNontechnology alternative: {c.nontechnology_alternative}')
    for i in c.issues: text.append(f'**{i.category} · {i.severity}:** {i.concern}\n\nAction: {i.action} '+', '.join(f'[{eid}]' for eid in i.evidence_ids))
    text.extend(['## 15. Areas Requiring Additional Research\n'+bullet(r.additional_research+s.research.gaps), '## 16. Sources'])
    for e in s.approved: text.append(f'- {e.id}: [{e.source_title}]({e.source_url}). Published: {e.publication_date or "unknown"}.')
    registry = {e.id:str(e.source_url) for e in s.approved}
    return re.sub(r'\[(E\d+)\](?!\()', lambda m: f'[{m[1]}]({registry[m[1]]})' if m[1] in registry else m[0], '\n\n'.join(text))
