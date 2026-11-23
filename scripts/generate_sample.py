"""Reproduce deterministic outputs and a real demo event log without an API key."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from workflow import Session
from logging_utils import AuditLog
from report import build_report
import demo
ROOT=Path(__file__).resolve().parents[1]

def main():
    log=AuditLog(ROOT/'logs');s=Session('Demo')
    log.write('challenge_submitted',mode='Demo',challenge=demo.CHALLENGE.model_dump())
    s.set_research(demo.CHALLENGE,demo.research());log.write('research_completed',mode='Demo',result=s.research.model_dump(mode='json'))
    s.approve(['E1','E2','E3']);log.write('human_evidence_approval',included=s.approved_ids,excluded=['E4'],actor='scripted demonstration')
    s.opportunities=demo.opportunities(s.approved);log.write('opportunities_generated',mode='Demo',result=s.opportunities.model_dump())
    s.choose(['O1'],'O1','Prioritize mechanic workload and a reversible pilot.');log.write('human_opportunity_review',selected=s.selected_ids,rejected=['O2','O3'],deep_dive=s.deep_id,feedback=s.feedback,actor='scripted demonstration')
    s.roadmap=demo.roadmap(s.selected,s.deep_id,s.feedback);log.write('roadmap_generated',mode='Demo',result=s.roadmap.model_dump())
    s.critique=demo.critic(s.roadmap);log.write('critic_completed',mode='Demo',result=s.critique.model_dump())
    (ROOT/'sample_outputs'/'aviation_strategy_brief.md').write_text(build_report(s,log.session_id),encoding='utf-8')
    (ROOT/'sample_outputs'/'demo_session.json').write_text(log.export(),encoding='utf-8')
    print('Sample brief and executed demo log saved.')

if __name__=='__main__':main()
