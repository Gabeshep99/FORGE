from pathlib import Path
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'

def button(app,label): return next(b for b in app.button if b.label==label)

def test_ui_demo_to_report(tmp_path,monkeypatch):
    monkeypatch.setenv('FORGE_LOG_DIR',str(tmp_path))
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not at.exception
    button(at,'Research Opportunity').click().run()
    assert not at.exception and at.session_state.workflow.research
    # Exclude GE evidence: its opportunity must disappear.
    at.checkbox[3].uncheck()
    button(at,'Approve Evidence & Continue').click().run()
    button(at,'Generate Technology Opportunities').click().run()
    assert not at.exception
    assert len(at.session_state.workflow.opportunities.opportunities)==3
    at.text_area[-1].set_value('Prioritize mechanic workload')
    button(at,'Approve Selection & Build Roadmap').click().run()
    assert not at.exception and at.session_state.workflow.roadmap
    button(at,'Run Independent AI Strategy Review').click().run()
    assert not at.exception and at.session_state.workflow.critique
    button(at,'Continue to final strategy brief →').click().run()
    assert not at.exception
    assert len(at.get('download_button'))>=3
    # Reapproval invalidates the final brief (navigate back to Evidence).
    at.session_state.active_step=1
    at.run()
    button(at,'Approve Evidence & Continue').click().run()
    assert at.session_state.workflow.critique is None
