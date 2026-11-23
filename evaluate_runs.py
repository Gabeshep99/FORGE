"""Offline quality and cost evaluation on exported FORGE session logs.

No model calls. Does not claim factual accuracy or strategy quality automatically.
"""
import argparse, csv, json
from pathlib import Path

def inspect_file(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    events=data.get("events", data) if isinstance(data,dict) else data
    if not isinstance(events,list):
        raise ValueError("Expected a list of event records or an object with events.")
    names=[e.get("event",e.get("type","")) for e in events if isinstance(e,dict)]
    def n(term):
        return sum(term in str(name) for name in names)
    return {
        "file": str(path),
        "events":len(events),
        "api_requests":n("api_request"),
        "api_responses":n("api_response"),
        "api_errors":n("api_error"),
        "research_completed":n("research_completed"),
        "opportunities_generated":n("opportunities_generated"),
        "roadmap_generated":n("roadmap_generated"),
        "critic_completed":n("critic_completed"),
        "human_evidence_approval":n("human_evidence_approval"),
        "human_opportunity_review":n("human_opportunity_review"),
        "complete":int(all(n(x)>0 for x in (
            "research_completed","opportunities_generated","roadmap_generated","critic_completed"))),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("logs",nargs="+",help="Exported FORGE session JSON logs")
    p.add_argument("--out",default="forge_evaluation.csv")
    args=p.parse_args()
    rows=[inspect_file(x) for x in args.logs]
    with open(args.out,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} run(s) to {args.out}")
    print("NOTE: Human rubric scores and factual verification still required.")

if __name__=="__main__": main()
