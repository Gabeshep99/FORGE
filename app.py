"""Run with: python -m streamlit run app.py"""
import os
import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError
from schemas import Challenge
from workflow import Session
from logging_utils import AuditLog
from agents import Agents, WorkflowError
from cost_control import UsageLedger
from model_advisor import PROFILES, MODEL_OPTIONS, profile_caps, rough_total_cost
from report import build_report
from forge_theme import render_intro, nav
from forge_pdf import build_pdf
from methodology import rubric_markdown
import demo
from context_check import context_warnings

load_dotenv()
st.set_page_config(page_title='FORGE | Technology Strategy', page_icon='◈', layout='wide')

# Community Cloud secrets are read only server-side and never copied into logs.
try:
    if not os.getenv('OPENAI_API_KEY') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    if not os.getenv('OPENAI_MODEL') and 'OPENAI_MODEL' in st.secrets:
        os.environ['OPENAI_MODEL'] = st.secrets['OPENAI_MODEL']
except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
    pass

# FORGE_COST_UPGRADE: one ledger per Streamlit session, preserved across reruns.
if 'cost_ledger' not in st.session_state: st.session_state.cost_ledger = UsageLedger()
if 'audit' not in st.session_state: st.session_state.audit = AuditLog()
if 'workflow' not in st.session_state: st.session_state.workflow = Session(mode='Demo')
s, log = st.session_state.workflow, st.session_state.audit

with st.sidebar:
    st.title('◈ FORGE')
    st.caption('Technology strategy, with evidence.')
    mode = st.radio('Workspace mode', ['Demo','Live'], disabled=s.research is not None,
                    help='Demo is a fixed public aviation case. Live researches the challenge you enter.')
    s.mode = mode
    st.caption('Assign models by agent; research has two calls, strategy has two, critic has one.')
    model_profile = st.selectbox('AI model recommendation', list(PROFILES), index=1,
        help='Budget saver reduces costs; Balanced is the recommended default; Higher reliability increases output and reasoning room.',
        disabled=mode=='Demo')
    profile_data = PROFILES[model_profile]
    st.caption(profile_data['note'])
    base = profile_data['models']
    researcher_model = st.selectbox('Researcher model', MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(base['Researcher']), key='researcher_'+model_profile, disabled=mode=='Demo')
    strategist_model = st.selectbox('Strategist model', MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(base['Strategist']), key='strategist_'+model_profile, disabled=mode=='Demo')
    critic_model = st.selectbox('Critic model', MODEL_OPTIONS,
        index=MODEL_OPTIONS.index(base['Critic']), key='critic_'+model_profile, disabled=mode=='Demo')
    selected_models = {'Researcher':researcher_model,'Strategist':strategist_model,'Critic':critic_model}
    caps = profile_caps(model_profile)
    st.caption('Output ceilings (tokens): ' + ', '.join(
        f'{k.split("/")[-1]} {v:,}' for k,v in caps.items()))
    st.caption(f'Rough full-run planning estimate: ${rough_total_cost(selected_models, caps):.3f}. '
               'Assumes 7,000 input tokens per stage and two web calls; actual costs vary.')
    st.session_state.cost_ledger.budget = st.number_input(
        'Estimated per-session cost safeguard (USD)',min_value=0.05,max_value=20.0,
        value=float(st.session_state.cost_ledger.budget),step=0.05,disabled=mode=='Demo')
    st.metric('Estimated session API spend',f"${st.session_state.cost_ledger.total:.4f}")
    st.caption('Prices estimated from standard token rates and web search allowance, not an enforceable billing cap. Set organization-level API spending limits separately.')
    if st.session_state.cost_ledger.records:
        with st.expander('API usage breakdown'):
            st.dataframe(st.session_state.cost_ledger.records,hide_index=True)
    st.caption('Live: up to five API requests in an initial run; no automatic retries.')
    if st.button('Start new session'):
        for key in list(st.session_state): del st.session_state[key]
        st.rerun()
    st.download_button('Export session log', log.export(), f'forge-session-{log.session_id}.json', 'application/json', key='sidebar_log')
    st.caption('Download your log before starting over or closing the tab. Browser refresh can reset the workspace.')
    st.divider()
    st.caption('DECISION PROCESS')
    for label,done in [('Define challenge',s.challenge),('Review evidence',s.approved_ids),('Evaluate opportunities',s.opportunities),('Human decision',s.selected_ids),('Build roadmap',s.roadmap),('Challenge strategy',s.critique)]:
        st.write(('✓ ' if done else '○ ')+label)

render_intro()
if mode=='Demo': st.info('OFFLINE EXAMPLE · Aerospace is the included sample challenge. FORGE supports any industry in Live mode. Demo outputs are prewritten and make no API calls. Public research was checked September 30, 2026.')
else: st.info('LIVE RESEARCH · Public information only. Your challenge, approved evidence and feedback are sent to OpenAI. Review every source before approving.')
if log.persistence_error: st.warning(log.persistence_error)
progress = sum(bool(x) for x in [s.challenge,s.approved_ids,s.opportunities,s.selected_ids,s.roadmap,s.critique])
st.progress(progress/6, text=f'{progress} of 6 decision milestones complete')
cols = st.columns(3)
cols[0].metric('Evidence approved',len(s.approved_ids))
cols[1].metric('Opportunities explored',len(s.opportunities.opportunities) if s.opportunities else 0)
cols[2].metric('Review status',s.critique.verdict if s.critique else 'Pending')


def run_action(action, next_step=None):
    try:
        with st.spinner('Working on this stage…'):
            action()
        if next_step is not None:
            st.session_state.active_step = next_step
        st.rerun()
    except WorkflowError as exc:
        log.write('workflow_error',message=str(exc))
        st.error(str(exc))
    except ValidationError:
        st.error('Check required fields: organization and industry need at least 2 characters; describe the challenge in at least 15 characters.')
    except Exception as exc:
        log.write('unexpected_error',error_type=type(exc).__name__)
        st.error('This stage could not complete. Existing results are preserved. Export the log and retry; check server logs if the issue continues.')


def agent(): return Agents(log, models=selected_models,
                           ledger=st.session_state.cost_ledger, profile=model_profile)

def sources(ids):
    for e in s.approved:
        if e.id in ids: st.markdown(f'[{e.id} · {e.source_title}]({e.source_url})')


current_step = nav()
if current_step == 0:
    st.subheader('Define the strategic problem')
    st.write('Choose a problem and planning horizon. FORGE researches options before proposing an implementation.')
    with st.form('challenge_form'):
        left,right=st.columns(2)
        defaults = demo.CHALLENGE if mode == 'Demo' else None
        org=left.text_input('Company or organization',value=defaults.organization if defaults else '',disabled=mode=='Demo',max_chars=200,key=f'org_{mode}')
        industry=right.text_input('Industry',value=defaults.industry if defaults else '',disabled=mode=='Demo',max_chars=200,key=f'industry_{mode}')
        problem=st.text_area('Strategic challenge',value=defaults.challenge if defaults else '',disabled=mode=='Demo',max_chars=6000,key=f'problem_{mode}')
        horizon=st.text_input('Planning horizon',value=defaults.horizon if defaults else '',disabled=mode=='Demo',max_chars=100,key=f'horizon_{mode}')
        context=st.text_area('Additional context (optional)',value=defaults.context if defaults else '',disabled=mode=='Demo',max_chars=6000,key=f'context_{mode}')
        confirm_context=st.checkbox('I confirm any cross-industry context is intentional',value=False,disabled=mode=='Demo',key=f'confirm_{mode}')
        submitted=st.form_submit_button('Research Opportunity',type='primary')
    if submitted:
        warnings = context_warnings(org, industry, problem, context) if mode=='Live' else []
        if warnings and not confirm_context:
            for warning in warnings: st.warning(warning)
            st.error('No API call was made. Correct your inputs, or tick the confirmation checkbox and resubmit.')
        else:
            def research_action():
                ch=Challenge(organization=org,industry=industry,challenge=problem,horizon=horizon,context=context)
                log.write('challenge_submitted',mode=mode,challenge=ch.model_dump())
                result=demo.research() if mode=='Demo' else agent().research(ch)
                s.set_research(ch,result)
                log.write('research_completed',mode=mode,result=result.model_dump(mode='json'))
            run_action(research_action, 1)
    if s.research: st.success('Research ready. Open “2 · Evidence” to inspect and approve findings.')

if current_step == 1:
    st.subheader('Human gate 1 · Review the evidence')
    st.caption('Review source support, date, relevance and limitations. Source identity checks do not prove the source supports the claim. Changes take effect when you submit approval.')
    if not s.research: st.info('Research a challenge first.')
    else:
        with st.expander('Coverage gaps',expanded=True):
            for gap in s.research.gaps: st.write('• '+gap)
        with st.form(f'evidence_form_{s.revision}'):
            included=[]
            for e in s.research.findings:
                with st.container(border=True):
                    st.markdown(f'**{e.id} · {e.finding}**')
                    st.write(e.explanation)
                    st.markdown(f'[{e.source_title}]({e.source_url})')
                    st.caption(f'{e.category} · Published: {e.publication_date or "Unknown"} · Strength: {e.strength}')
                    st.write('**Why this strength:** '+e.strength_reason)
                    st.write('**Relevance:** '+e.relevance)
                    st.write('**Limitation:** '+e.limitation)
                    if st.checkbox('Include finding',value=e.id in s.approved_ids if s.approved_ids else True,key=f'include_{s.revision}_{e.id}'): included.append(e.id)
            approve=st.form_submit_button('Approve Evidence & Continue',type='primary')
        if approve:
            def approve_action():
                s.approve(included)
                log.write('human_evidence_approval',included=included,excluded=[e.id for e in s.research.findings if e.id not in included])
            run_action(approve_action, 1)
        if s.approved_ids:
            st.success(f'{len(s.approved_ids)} findings approved. Opportunity generation uses only this approved snapshot.')
            if st.button('Generate Technology Opportunities',type='primary'):
                def opportunity_action():
                    result=demo.opportunities(s.approved) if mode=='Demo' else agent().opportunities(s.challenge,s.approved)
                    s.opportunities=result
                    s.clear_strategy()
                    log.write('opportunities_generated',mode=mode,result=result.model_dump())
                run_action(opportunity_action, 2)

if current_step == 2:
    st.subheader('Technology opportunities & strategic evaluation')
    with st.expander('Transparent assessment criteria'):
        st.markdown(rubric_markdown())
    if not s.opportunities: st.info('Approve evidence and generate opportunities first.')
    else:
        st.caption('These are research options, not validated business cases. High risk, difficulty, impact or time does not mean a better option.')
        rows=[]
        for o in s.opportunities.opportunities:
            rows.append({'Opportunity':o.name,**{a.dimension:a.rating for a in o.assessments}})
            with st.expander(f'{o.id} · {o.name}',expanded=False):
                for title,text in [('Problem addressed',o.problem_addressed),('Technology',o.technology),('How it works',o.how_it_works),('Business-value hypothesis',o.business_value_hypothesis),('Maturity',o.maturity+' — '+o.maturity_reason),('Competitive implications',o.competitive_implications),('Implementation estimate',o.time_horizon_estimate)]:
                    st.markdown(f'**{title}**'); st.write(text)
                st.write('**Barriers:** '+ '; '.join(o.barriers))
                sources(o.evidence_ids)
                for a in o.assessments:
                    st.write(f'**{a.dimension} · {a.rating}:** {a.reason}')
                    if a.evidence_ids: sources(a.evidence_ids)
        st.dataframe(rows,hide_index=True,width='stretch')
        st.subheader('Human gate 2 · Make the strategy decision')
        choices={o.id:o.name for o in s.opportunities.opportunities}
        with st.form(f'selection_{s.revision}'):
            selection=st.multiselect('Opportunities to include',options=list(choices),default=s.selected_ids or [next(iter(choices))],format_func=lambda x: choices[x])
            deep=st.selectbox('Opportunity for deeper implementation analysis',options=list(choices),format_func=lambda x: choices[x],index=list(choices).index(s.deep_id) if s.deep_id else 0)
            feedback=st.text_area('Comments and priorities',value=s.feedback,placeholder='For example: prioritize a low-cost pilot, mechanic workload and data access.',max_chars=6000)
            choose=st.form_submit_button('Approve Selection & Build Roadmap',type='primary')
        if choose:
            def roadmap_action():
                s.choose(selection,deep,feedback)
                log.write('human_opportunity_review',selected=selection,rejected=[i for i in choices if i not in selection],deep_dive=deep,feedback=feedback)
                result=demo.roadmap(s.selected,s.deep_id,s.feedback) if mode=='Demo' else agent().roadmap(s.challenge,s.approved,s.selected,s.deep_id,s.feedback)
                s.roadmap=result
                log.write('roadmap_generated',mode=mode,result=result.model_dump())
            run_action(roadmap_action, 3)

if current_step == 3:
    st.subheader('Initial implementation roadmap')
    if not s.roadmap: st.info('Select opportunities and submit your priorities first.')
    else:
        r=s.roadmap
        st.write(r.executive_summary)
        st.markdown('**Strategic objective**'); st.write(r.strategic_objective)
        st.markdown('**Why this matters**'); st.write(r.why_it_matters); sources(r.evidence_ids)
        st.markdown('**Proposed pilot**'); st.write(r.proposed_pilot)
        st.info('Response to your priorities: '+r.feedback_response)
        for title,values in [('Required capabilities',r.required_capabilities),('Key stakeholders',r.stakeholders),('Data requirements',r.data_requirements),('Human factors',r.human_factors),('Technical requirements',r.technical_requirements)]:
            with st.expander(title):
                for v in values: st.write('• '+v)
        for p in r.phases:
            with st.container(border=True):
                st.markdown(f'**{p.name}** · {p.duration_estimate}')
                for a in p.actions: st.write('• '+a)
                st.caption('Owner: '+p.owner)
                st.write('**Exit gate:** '+p.exit_gate)
        st.markdown('**Proposed KPIs — measure before claiming impact**')
        st.dataframe([k.model_dump() for k in r.kpis],hide_index=True,width='stretch')
        with st.expander('Assumptions and additional research'):
            for value in r.assumptions+r.additional_research: st.write('• '+value)
        if st.button('Run Independent AI Strategy Review',type='primary'):
            def critic_action():
                result=demo.critic(s.roadmap) if mode=='Demo' else agent().critic(s.challenge,s.approved,s.selected,s.roadmap,s.feedback)
                s.critique=result
                log.write('critic_completed',mode=mode,result=result.model_dump())
            run_action(critic_action, 4)

if current_step == 4:
    st.subheader('Independent AI Strategy Review')
    st.caption('A separate adversarial review. In live mode it uses a fresh request, but the same model/provider may share blind spots. Demo review is a fixed checklist.')
    if not s.critique: st.info('Build the roadmap, then run the review.')
    else:
        c=s.critique
        st.warning(c.verdict+' · '+c.summary)
        if st.button('Continue to final strategy brief →',type='primary'):
            st.session_state.active_step = 5
            st.rerun()
        st.markdown('**Strongest counterargument**');st.write(c.strongest_counterargument)
        st.markdown('**Nontechnology alternative**');st.write(c.nontechnology_alternative)
        for i in c.issues:
            with st.expander(f'{i.severity} · {i.category}',expanded=i.severity=='High'):
                st.write(i.concern); st.write('**Action:** '+i.action); sources(i.evidence_ids)
        st.info('To revise: return to Opportunities, add the concerns to your priorities, rebuild the roadmap, and rerun the critic. The final brief preserves unresolved criticism.')

if current_step == 5:
    st.subheader('Final technology strategy brief')
    if not s.critique: st.info('The final brief unlocks after the critic review.')
    else:
        report=build_report(s,log.session_id)
        st.download_button('Download strategy brief (.md)',report,'FORGE_strategy_brief.md','text/markdown',type='primary')
        st.download_button('Download strategy brief (.pdf)',build_pdf(report),'FORGE_strategy_brief.pdf','application/pdf')
        st.download_button('Download full audit log (.json)',log.export(),f'forge-session-{log.session_id}.json','application/json')
        st.caption('The brief has 16 sections, linked evidence, assessments, your selections, roadmap, KPI definitions and the full critic review.')
        with st.expander('Preview complete brief',expanded=False): st.markdown(report)
