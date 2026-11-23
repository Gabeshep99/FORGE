"""Curated, deterministic demonstration. No live AI results are represented here."""
from schemas import *
from agents import WorkflowError, validate_opportunities
from methodology import RUBRIC

CHALLENGE = Challenge(organization='Commercial Aviation Company', industry='Commercial Aviation',
 challenge='Reduce aircraft maintenance downtime and disruption caused by difficult-to-source engine/APU components.',
 horizon='3–10 years', context='Public-information portfolio scenario. Begin with a bounded, advisory-only pilot.')


def research():
    data = [
      ('E1', 'NASA describes simulated engine degradation data.', 'The dataset models engine behavior and faults; it is not a field trial.', 'Technology',
       'C-MAPSS Aircraft Engine Simulator Data — NASA', 'https://data.nasa.gov/dataset/c-mapss-aircraft-engine-simulator-data', '2010-09-22',
       'Could inform an initial prognostics benchmark.', 'Simulator transfer to real fleets is unproven; the catalog currently reports download unavailability.'),
      ('E2', 'Digital twin credibility requires validation and uncertainty assessment.', 'NIST describes lifecycle credibility assessment for manufacturing twins.', 'Technology',
       'Credibility Consideration for Digital Twins in Manufacturing — NIST', 'https://www.nist.gov/publications/credibility-consideration-digital-twins-manufacturing', '2022-12-16',
       'Provides a validation lens for a proposed maintenance twin.', 'Manufacturing methodology does not establish an aviation deployment or downtime benefit.'),
      ('E3', 'Airbus reported initial Skywise Health Monitoring operations with Allegiant.', 'Its announcement describes bringing diagnostic alerts and maintenance information together.', 'Competition',
       'Airbus launches Skywise Health Monitoring with Allegiant Air', 'https://www.airbus.com/en/newsroom/press-releases/2019-04-airbus-launches-skywise-health-monitoring-with-us-airline-allegiant', '2019-04',
       'Shows an adjacent commercial precedent for maintenance decision support.', 'Vendor announcement; no independent causal evidence of local savings.'),
      ('E4', 'GE reported mass production of additive fuel nozzle tips.', 'The historical example concerns a specific engine component and production process.', 'Industry',
       'Manufacturing Milestone: 30,000 Additive Fuel Nozzles — GE Aerospace', 'https://www.geaerospace.com/news/articles/manufacturing/manufacturing-milestone-30000-additive-fuel-nozzles', '2018-10-04',
       'Motivates investigating component-specific manufacturing alternatives.', 'Does not establish feasibility, approval, or economics for arbitrary replacement blades or APU parts.')
    ]
    return Research(findings=[Evidence(id=i,finding=f,explanation=x,category=c,source_title=t,source_url=u,
        publication_date=d,strength='Medium',strength_reason='Primary description supports this narrow finding; local outcomes are unverified.',
        relevance=r,limitation=l) for i,f,x,c,t,u,d,r,l in data], gaps=[
        'The organization is fictional; its strategy, fleet, budgets and business model were not researched.',
        'Current component lead times, downtime drivers and supplier alternatives need fresh research.',
        'This curated historical fixture is not a comprehensive current market scan.',
        'Readiness for the exact application and independent outcome evidence remain unverified.'])

SPECS = [
 ('O1','E1','Engine-health forecasting benchmark','Unplanned maintenance and uncertain replacement timing',
  'Data-driven prognostics with uncertainty estimates','Estimate deterioration from historical sensor patterns, then test predictions against held-out outcomes.',
  'Demonstrated prototype','Simulator-based research precedent; local fleet deployment has not been established.',
  'Earlier warnings might allow planners to prepare parts and labor. No savings have been measured.',
  ['Representative labeled fleet data','Domain shift from simulation','False alarms and missed failures'], 'Estimated 1–3 years to a bounded advisory deployment after validation.'),
 ('O2','E2','Validated maintenance digital twin','Difficulty comparing maintenance actions and failure scenarios',
  'A component model linked to operational data and uncertainty estimates','Test hypothetical maintenance choices against a calibrated model and display uncertainty to engineers.',
  'Academic research','Application-specific readiness is unknown; the cited source establishes a credibility methodology.',
  'Scenario testing might improve maintenance planning; model maintenance costs may exceed the benefit.',
  ['Model calibration and validation','Configuration history','Data and model ownership'], 'Estimated over 3 years for a qualified component-specific deployment; research milestones come first.'),
 ('O3','E3','Maintenance-event and parts-readiness support','Slow coordination after technical events',
  'Integrated diagnostic and maintenance information with planner review','Bring alerts, work history and a proposed parts-availability view into one planning workflow.',
  'Early commercialization','Historical health-monitoring deployment is documented; the proposed local integration is unvalidated.',
  'Could reduce planner search time and coordination delays. Compare with improving existing procedures.',
  ['Maintenance-system integration','Inventory data quality','Human accountability'], 'Estimated 1–3 years to a bounded deployment, contingent on access and integration.'),
 ('O4','E4','Component-specific additive feasibility study','Dependence on difficult-to-source components',
  'Additive manufacturing process and qualification analysis','Screen a single component for manufacturing feasibility before considering prototype production.',
  'Academic research','The proposed replacement component is unspecified; another nozzle is a commercial precedent, not proof of local readiness.',
  'A qualified alternate process could expand sourcing options; total cost and approval burden remain unknown.',
  ['Design rights and qualification route','Material and fatigue performance','Production economics'], 'Estimated over 3 years to a qualified flight component, if feasibility is established.')
]

def opportunities(approved):
    ids = {e.id for e in approved}
    out = []
    for oid,eid,name,problem,tech,how,maturity,mwhy,value,barriers,horizon in SPECS:
        if eid not in ids: continue
        ratings = {'Stakeholder value':'Medium','Business value':'Medium','Technical feasibility':'Unknown',
          'Technology maturity':'Unknown','Implementation difficulty':'High','Differentiation':'Unknown',
          'Evidence strength':'Low','Human impact':'Medium','Risk':'High','Time to implementation':'Unknown'}
        reasons = {
          'Stakeholder value':'The proposed benefit is relevant, but users have not validated the workflow.',
          'Business value':'The value mechanism is plausible; no local baseline or net benefit has been measured.',
          'Implementation difficulty':'The proposal requires new data integration, specialist skills or qualification work.',
          'Evidence strength':'The available description motivates investigation but does not prove the proposed local outcome.',
          'Human impact':'The proposed pilot adds review tasks and training while retaining human authority.',
          'Risk':'Unresolved transfer and validation questions require an offline pilot before any operational use.'}
        assessments = [Assessment(dimension=d,rating=ratings[d],reason=reasons.get(d,'Unknown: the approved source does not establish this dimension for the exact application.'), evidence_ids=[eid] if ratings[d]!='Unknown' else []) for d in DIMENSIONS]
        out.append(Opportunity(id=oid,name=name,problem_addressed=problem,technology=tech,how_it_works=how,
          evidence_ids=[eid],business_value_hypothesis=value,maturity=maturity,maturity_reason=mwhy,
          competitive_implications='Differentiation is unproven. Owning the workflow and learning from users may matter more than buying a common technology.',
          barriers=barriers,time_horizon_estimate=horizon,assessments=assessments))
    if len(out)<3: raise WorkflowError('This fixed demo has fewer than three supported options after your exclusions. Include at least three findings or use Live research for newly generated options. Excluded evidence will not be reused.')
    return validate_opportunities(Opportunities(opportunities=out), approved)


def roadmap(selected, deep_id, feedback):
    o = next(o for o in selected if o.id==deep_id)
    focus = {
     'O1': ('historical engine-health forecasts','Representative sensor histories, failures, censoring and operating conditions','Missed-event rate','Missed labeled events divided by all labeled events; also report false alarms and lead time.'),
     'O2': ('component-model scenario comparisons','Component configuration, inspection records and calibration data','Model discrepancy','Difference between predicted and held-out observed outcomes, with uncertainty coverage.'),
     'O3': ('maintenance-event coordination','Timestamped alerts, maintenance tasks and inventory availability','Planner time per event','Elapsed active planner minutes from event intake to a documented parts/maintenance plan.'),
     'O4': ('one component manufacturing feasibility assessment','Authorized geometry, material requirements and qualification criteria','Qualification evidence coverage','Required qualification evidence items completed divided by items agreed with the responsible specialists.')
    }[o.id]
    topic,data,kpi,definition = focus
    phases = [
      ('Validation',['Confirm the problem with planners and mechanics.','Establish the current-process comparator and baseline.','Review the submitted human priorities before agreeing scope.'],'Operations lead','Proceed only with an agreed problem, data rights, KPI definitions and review authority.','Estimated 2–4 weeks'),
      ('Prototype',[f'Build an offline prototype for {topic}.','Test data quality and representative failure cases.'],'Engineering lead','Proceed only after data and prototype limitations are documented and accepted.','Estimated 4–8 weeks'),
      ('Pilot',['Run a bounded, advisory-only comparison.','Keep current operational procedures in force; log recommendations, overrides and failures.'],'Pilot owner','Stop for any uncontrolled safety/data issue; require reviewer sign-off to continue.','Estimated 6–12 weeks'),
      ('Evaluation',['Compare against the baseline and process-only alternative.','Report uncertainty, total costs and negative outcomes.'],'Independent evaluator','Proceed only if pre-agreed criteria and stakeholder acceptance are met.','Estimated 2–4 weeks'),
      ('Scale Decision',['Decide stop, revise, extend or scale.','Fund support and monitoring only after approval.'],'Accountable sponsor','No scaling without approved evidence, cost case and a deployment-specific qualification review.','Estimated 2–4 weeks')]
    return Roadmap(executive_summary=f'Propose a bounded investigation of {o.name.lower()}. The cited precedent motivates a test, not a promise of reduced downtime.',
      strategic_objective=f'Test whether {topic} can improve a defined maintenance decision without reducing human accountability.',
      why_it_matters=f'The approved precedent [{o.evidence_ids[0]}] motivates investigation. Local business value remains a hypothesis.',
      evidence_ids=o.evidence_ids, proposed_pilot=f'Proposed pilot: evaluate {topic} offline against the current process; no flight-release or procurement automation.',
      required_capabilities=['Maintenance expertise','Data stewardship','Evaluation design','Applicable engineering specialists'],
      stakeholders=['Maintenance planners','Mechanics','Engineering','Procurement','Safety/quality','IT security','Finance','Accountable sponsor'],
      data_requirements=[data,'Documented consent/access authority, retention policy and provenance'],
      human_factors=['Co-design with affected users.','Record overrides without penalizing workers.','Measure workload and automation bias.'],
      technical_requirements=['Restricted prototype environment','Traceable input versions','Access controls','Rollback and monitoring plan'],
      phases=[Phase(name=n,actions=a,owner=w,exit_gate=g,duration_estimate=t) for n,a,w,g,t in phases],
      kpis=[KPI(name=kpi,definition=definition,baseline_plan='Collect a representative baseline before the pilot; no baseline is assumed.',measurement_method='Use versioned event records and an evaluator independent of the prototype builder.',decision_rule='Agree a meaningful improvement and uncertainty tolerance before testing; do not infer success from this proposal.'),
            KPI(name='Reviewer workload and overrides',definition='Review minutes per case and proportion of recommendations overridden, with reasons.',baseline_plan='Observe the current workflow with participating users.',measurement_method='Time logs, decision records and structured user debriefs.',decision_rule='Agree acceptable workload and safety boundaries before the pilot; investigate every harmful recommendation.')],
      assumptions=['Relevant data can be obtained lawfully.','The problem is materially affected by the chosen intervention.','Users have time and authority to review outputs.'],
      additional_research=['Verify the exact component and downtime causes.','Obtain current independent evidence and competitor comparisons.','Assess deployment-specific compliance with qualified personnel.'],
      feedback_response=('Demo limitation: your priority is retained as a validation agenda item: '+feedback if feedback else 'No additional priority was submitted; validate pilot scope with users.')+' Free-text semantic adaptation requires Live research mode.')


def critic(roadmap):
    categories = {
      'Unsupported claims':('No measured local benefit exists.','Do not present the value hypothesis as an achieved result.'),
      'Weak evidence':('The curated sources are sparse and partly historical.','Acquire current independent empirical evidence.'),
      'Hallucination risks':('A real source can be misapplied to a new component.','Verify each claim against the actual source and scope.'),
      'Assumptions':('Access to representative data is assumed.','Secure an approved data inventory before the prototype.'),
      'Missing stakeholders':('Named roles are not confirmed participants.','Obtain accountable owners and involve frontline users.'),
      'Human factors':('Reviewers may overtrust confident recommendations.','Evaluate calibration, workload and override behavior.'),
      'Data/privacy':('Data rights and retention rules are not established.','Complete a data-access and privacy review.'),
      'Ethics':('Performance tracking could become punitive worker surveillance.','Agree purpose limitations with affected staff.'),
      'Regulatory':('No component-specific qualification route has been established.','Have qualified safety and compliance staff determine requirements.'),
      'Adoption':('Another dashboard may add work without changing decisions.','Compare workflow fit with existing tools.'),
      'Alternative explanations':('Parts scarcity could dominate downtime regardless of prediction quality.','Analyze delay causes and compare inventory/process changes.'),
      'Evidence needed':('Baseline and decision thresholds are absent.','Specify the baseline and acceptance rules before the trial.'),
      'Failure modes':('Distribution shift, missing data or false alerts may invalidate results.','Test realistic negative cases and stop conditions.')}
    return Critique(verdict='Revise before pilot',summary='The proposed direction is a testable hypothesis, but local evidence and accountable approval are missing.',
      issues=[CritiqueItem(category=c,severity='High' if c in ('Unsupported claims','Regulatory','Data/privacy','Failure modes') else 'Medium',concern=v[0],action=v[1],evidence_ids=[]) for c,v in categories.items()],
      strongest_counterargument='Downtime may be constrained by supply and repair capacity rather than information; the proposed tool could add cost without removing that bottleneck.',
      nontechnology_alternative='Compare better parts stocking, pooling agreements and clearer maintenance handoffs before committing to a new technology.')
