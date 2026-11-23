"""FORGE visual identity, hero, and workflow navigation (no external assets)."""
import streamlit as st

STEPS = ['Challenge', 'Evidence', 'Opportunities', 'Roadmap', 'Critic', 'Final brief']

CSS = '''
<style>
:root { color-scheme:dark; }
.stApp {
  background: radial-gradient(ellipse 1100px 500px at 78% -80px, rgba(24,104,136,.22), transparent 70%),
              radial-gradient(ellipse 730px 350px at 0% 15%, rgba(47,117,120,.12), transparent 70%),
              #090f1a;
  color: #e8f3fa;
}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:#0c1725;border-right:1px solid #254357}
.block-container{max-width:1300px;padding-top:2rem;padding-bottom:5rem}
h1,h2,h3{letter-spacing:-.035em;color:#edf8ff !important}
p,div,label{color:inherit}
[data-testid="stMetric"]{background:#101f2f;border:1px solid #24445a;border-radius:15px;padding:17px}
[data-testid="stMetricValue"]{color:#a9fbe8 !important}
[data-testid="stExpander"], [data-testid="stForm"]{background:rgba(15,29,45,.7);border:1px solid #263d54;border-radius:14px}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{
  color:#06141b;background:linear-gradient(105deg,#7df5d8,#a6dfff);border:0;border-radius:10px;
  font-weight:700;box-shadow:0 4px 20px rgba(74,201,199,.17)
}
.stButton>button:not([kind="primary"]),.stDownloadButton>button{border:1px solid #32516a;border-radius:10px}
[data-testid="stAlert"]{border-radius:13px}
.forge-hero{background:linear-gradient(120deg,rgba(13,35,53,.98),rgba(17,42,58,.86) 63%,rgba(14,50,60,.83));border:1px solid #2b6475;border-radius:22px;padding:36px 40px;margin:0 0 24px;box-shadow:0 15px 55px rgba(1,10,20,.25)}
.forge-eyebrow{font-size:11px;letter-spacing:.22em;font-weight:800;color:#88ebdd;margin-bottom:14px}
.forge-hero h1{font-size:clamp(36px,4vw,60px);line-height:1.04;margin:0 0 14px;color:#f6fcff}
.forge-hero h1 span{color:#85edd5}
.forge-hero .lead{max-width:900px;color:#d6e9f3;font-size:18px;line-height:1.65;margin:0 0 20px}
.forge-hero .case{font-size:14px;color:#aac4d0;line-height:1.55;margin:0}
.forge-pills{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 19px}
.forge-pills span{padding:5px 11px;border:1px solid #376577;border-radius:50px;font-size:12px;color:#d0f7f1;background:rgba(47,104,119,.16)}
.forge-flow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0 26px}
.forge-flow>div{border:1px solid #244155;background:rgba(17,32,49,.85);border-radius:14px;padding:16px}
.forge-flow b{color:#9bf4df;font-size:14px}.forge-flow p{font-size:12px;color:#b6cbd6;margin:6px 0 0}
@media(max-width:800px){.forge-hero{padding:22px}.forge-flow{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>'''

HERO = '''
<section class="forge-hero">
<div class="forge-eyebrow">FORGE / TECHNOLOGY STRATEGY WORKBENCH</div>
<h1>From complex problems to <span>decisions worth making.</span></h1>
<p class="lead">FORGE helps consultants, product teams, startups, and organizations decide which emerging technologies are worth investigating. Start with a real business challenge; review traceable research; compare strategic opportunities; then build a testable implementation roadmap with independent risk review.</p>
<div class="forge-pills"><span>Evidence before recommendations</span><span>Human-approved decisions</span><span>Multi-agent research & strategy</span><span>Auditable outputs</span></div>
<p class="case"><strong>Example use cases:</strong> A manufacturer evaluating predictive maintenance; a hospital improving administrative workflows; a startup exploring a new AI-enabled product; an aerospace company forecasting component shortages. Aviation is only the included offline example—not a restriction.</p>
</section>
<section class="forge-flow">
 <div><b>01 · Define</b><p>Describe your organization, goal, context, and constraints.</p></div>
 <div><b>02 · Validate</b><p>Researcher gathers sources; you approve relevant evidence.</p></div>
 <div><b>03 · Decide</b><p>Strategist evaluates opportunities; you select a direction.</p></div>
 <div><b>04 · Stress-test</b><p>Critic reviews a phased roadmap; export the brief and audit trail.</p></div>
</section>
'''

def render_intro():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(HERO, unsafe_allow_html=True)

def nav():
    if 'active_step' not in st.session_state:
        st.session_state.active_step = 0
    options=list(range(6))
    # Keep widget state separate from navigation state. Streamlit forbids changing
    # an instantiated widget's own key after it has been rendered.
    st.session_state.stage_picker = st.session_state.active_step
    def pick_stage():
        st.session_state.active_step = st.session_state.stage_picker
    current=st.segmented_control('Workflow stage',options=options,
       format_func=lambda i:f'{i+1:02d}  {STEPS[i]}',
       selection_mode='single',key='stage_picker',on_change=pick_stage)
    return current if current is not None else 0
