"""Real SDK serialization/parsing through a mock HTTP transport; no API charges."""
import json
import httpx
import pytest
from openai import OpenAI
from agents import Agents, WorkflowError
from schemas import Research
from logging_utils import AuditLog
import demo

def body(text, annotations=None, status='completed'):
    return {'id':'resp_test','object':'response','created_at':1,'status':status,'model':'test-model',
      'output':[{'id':'msg_test','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':text,'annotations':annotations or []}]}],
      'parallel_tool_calls':True,'tool_choice':'auto','tools':[],'usage':{'input_tokens':10,'output_tokens':10,'total_tokens':20},'error':None,'incomplete_details':None}

def client(handler):return OpenAI(api_key='sk-test-not-real',http_client=httpx.Client(transport=httpx.MockTransport(handler),trust_env=False),max_retries=0)

def test_current_sdk_research_wire_format(tmp_path):
    requests=[]
    def handler(req):
        data=json.loads(req.content);requests.append(data)
        if len(requests)==1:
            annotations=[{'type':'url_citation','url':str(e.source_url),'title':e.source_title,'start_index':0,'end_index':3} for e in demo.research().findings]
            return httpx.Response(200,json=body('Source narrative',annotations))
        return httpx.Response(200,json=body(demo.research().model_dump_json()))
    a=Agents(AuditLog(tmp_path),client=client(handler),model='gpt-6.1-terra')
    assert len(a.research(demo.CHALLENGE).findings)==4
    assert requests[0]['tools']==[{'type':'web_search'}]
    assert requests[0]['tool_choice']=='required' and requests[0]['store'] is False
    assert requests[1]['text']['format']['type']=='json_schema'
    assert requests[1]['text']['format']['strict'] is True
    assert len(a.log.events)==6
    assert len([e for e in a.log.events if e['event']=='api_usage'])==2
    assert 'sk-test-not-real' not in a.log.export()

@pytest.mark.parametrize('status,word',[(429,'quota'),(401,'authentication'),(500,'failed')])
def test_api_errors(tmp_path,status,word):
    a=Agents(AuditLog(tmp_path),client=client(lambda r:httpx.Response(status,json={'error':{'message':'failure','type':'test'}})))
    with pytest.raises(WorkflowError,match=word):a.call('test','instruction',{})
    assert a.log.events[-1]['event']=='api_error'

def test_no_web_sources_blocks_research(tmp_path):
    a=Agents(AuditLog(tmp_path),client=client(lambda r:httpx.Response(200,json=body('No sources'))))
    with pytest.raises(WorkflowError,match='no traceable'):a.research(demo.CHALLENGE)

def test_fabricated_source_blocked(tmp_path):
    count=0
    def handler(req):
        nonlocal count
        count+=1
        annotations=[{'type':'url_citation','url':'https://example.com/real','title':'Real','start_index':0,'end_index':3}]
        return httpx.Response(200,json=body('Evidence',annotations) if count==1 else body(demo.research().model_dump_json()))
    a=Agents(AuditLog(tmp_path),client=client(handler))
    with pytest.raises(WorkflowError,match='outside'):a.research(demo.CHALLENGE)

def test_malformed_json(tmp_path):
    a=Agents(AuditLog(tmp_path),client=client(lambda r:httpx.Response(200,json=body('{bad json'))))
    with pytest.raises(WorkflowError,match='invalid structured'):a.call('test','instruction',{},Research)

def test_missing_key(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with pytest.raises(WorkflowError,match='OPENAI_API_KEY'):Agents(AuditLog(tmp_path))

def test_only_approved_evidence_and_human_feedback_sent(tmp_path):
    approved=demo.research().findings[:3];options=demo.opportunities(approved);requests=[]
    roadmap=demo.roadmap(options.opportunities[:1],'O1','Budget first')
    outputs=[options.model_dump_json(),roadmap.model_dump_json(),demo.critic(roadmap).model_dump_json()]
    def handler(req):
        requests.append(json.loads(req.content));return httpx.Response(200,json=body(outputs.pop(0)))
    a=Agents(AuditLog(tmp_path),client=client(handler))
    result=a.opportunities(demo.CHALLENGE,approved)
    rm=a.roadmap(demo.CHALLENGE,approved,result.opportunities[:1],'O1','Budget first')
    a.critic(demo.CHALLENGE,approved,result.opportunities[:1],rm,'Budget first')
    for req in requests:
        data=json.loads(req['input'])
        assert {e['id'] for e in data['approved_evidence']}=={'E1','E2','E3'}
        assert 'previous_response_id' not in req
    assert json.loads(requests[1]['input'])['human_feedback']=='Budget first'
    assert 'adversarial' in requests[2]['instructions']

def test_timeout_is_actionable(tmp_path):
    def handler(req):raise httpx.ReadTimeout('timeout',request=req)
    a=Agents(AuditLog(tmp_path),client=client(handler))
    with pytest.raises(WorkflowError,match='timed out'):a.call('test','instruction',{})

def test_refusal_blocks_structured_stage(tmp_path):
    response=body('');response['output'][0]['content']=[{'type':'refusal','refusal':'Cannot assist'}]
    a=Agents(AuditLog(tmp_path),client=client(lambda req:httpx.Response(200,json=response)))
    with pytest.raises(WorkflowError,match='declined'):a.call('test','instruction',{},Research)
    assert a.log.events[-1]['event']=='api_response'

def test_incomplete_response_blocks_stage(tmp_path):
    response=body('partial',status='incomplete')
    response['incomplete_details']={'reason':'max_output_tokens'}
    a=Agents(AuditLog(tmp_path),client=client(lambda req:httpx.Response(200,json=response)))
    with pytest.raises(WorkflowError,match='incomplete'):a.call('test','instruction',{})

def test_invalid_output_is_preserved_in_audit(tmp_path):
    a=Agents(AuditLog(tmp_path),client=client(lambda req:httpx.Response(200,json=body('{bad json'))))
    with pytest.raises(WorkflowError):a.call('test','instruction',{},Research)
    responses=[e for e in a.log.events if e['event']=='api_response']
    assert responses[0]['response']['output'][0]['content'][0]['text']=='{bad json'
