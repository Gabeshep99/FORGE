import json
import pytest
from pydantic import ValidationError
from agents import WorkflowError, validate_opportunities, validate_refs, cited_sources
from schemas import Challenge
from workflow import Session
from logging_utils import AuditLog, redact
from report import build_report
import demo

@pytest.fixture
def session():
    s=Session('Demo'); s.set_research(demo.CHALLENGE,demo.research());return s

def complete(s):
    s.approve(['E1','E2','E3']);s.opportunities=demo.opportunities(s.approved)
    s.choose(['O1'],'O1','Prioritize workload')
    s.roadmap=demo.roadmap(s.selected,s.deep_id,s.feedback);s.critique=demo.critic(s.roadmap)
    return s

def test_end_to_end_report_excludes_rejected_evidence(session):
    complete(session);report=build_report(session,'test')
    assert report.count('\n## ')==16
    assert 'Prioritize workload' in report
    assert 'geaerospace.com' not in report
    assert 'NASA' in report and 'Revise before pilot' in report
    assert all(str(e.source_url) in report for e in session.approved)

def test_gate_and_stale_invalidation(session):
    with pytest.raises(WorkflowError):session.approve([])
    with pytest.raises(WorkflowError):session.choose(['O1'],'O1','')
    complete(session);session.approve(['E2'])
    assert not session.opportunities and not session.roadmap and not session.critique
    with pytest.raises(WorkflowError):build_report(session,'test')

def test_selection_must_include_deep_dive(session):
    complete(session)
    with pytest.raises(WorkflowError):session.choose(['O1'],'O2','')
    session.choose(['O2'],'O2','Changed priority')
    assert session.roadmap is None and session.critique is None

def test_new_research_clears_approval(session):
    complete(session);session.set_research(demo.CHALLENGE,demo.research())
    assert not session.approved and not session.selected and session.roadmap is None

def test_unsupported_references_and_missing_dimensions(session):
    complete(session)
    result=session.opportunities.model_copy(deep=True)
    result.opportunities[0].evidence_ids=['E999']
    with pytest.raises(WorkflowError):validate_opportunities(result,session.approved)
    with pytest.raises(WorkflowError):validate_refs({'claim':'Fact [E999]'}, {'E1'})
    result=session.opportunities.model_copy(deep=True);result.opportunities[0].assessments.pop()
    with pytest.raises(WorkflowError):validate_opportunities(result,session.approved)

def test_empty_input_is_invalid():
    data=demo.CHALLENGE.model_dump();data['organization']='  '
    with pytest.raises(ValidationError):Challenge(**data)

def test_secret_redaction_and_log_export(tmp_path, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','secret-test-value')
    log=AuditLog(tmp_path,'test')
    log.write('test',api_key='do-not-show',nested={'text':'secret-test-value sk-proj-123456789'},response='ok')
    output=log.export()
    assert 'secret-test-value' not in output and 'do-not-show' not in output and 'sk-proj-' not in output
    assert len(json.loads(output)['events'])==1
    assert json.loads((tmp_path/'test.jsonl').read_text())['response']=='ok'

def test_disk_failure_preserves_export(tmp_path):
    path=tmp_path/'file';path.write_text('x');log=AuditLog(path,'test');log.write('test')
    assert log.persistence_error and json.loads(log.export())['events']

def test_registry_requires_actual_annotations():
    assert cited_sources({'output':[{'type':'message','content':[{'text':'https://madeup.example','annotations':[]}]}]})=={}
    assert cited_sources({'output':[{'type':'message','content':[{'annotations':[{'type':'url_citation','url':'javascript:alert(1)','title':'bad'}]}]}]})=={}

def test_demo_exclusion_is_real(session):
    session.approve(['E1','E2','E3'])
    result=demo.opportunities(session.approved)
    assert len(result.opportunities)==3 and 'O4' not in [o.id for o in result.opportunities]
    session.approve(['E1'])
    with pytest.raises(WorkflowError):demo.opportunities(session.approved)
