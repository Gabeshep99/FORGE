"""Typed contracts shared by agents, UI, exports and validation."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Challenge(StrictModel):
    organization: str = Field(min_length=2, max_length=200)
    industry: str = Field(min_length=2, max_length=200)
    challenge: str = Field(min_length=15, max_length=6000)
    horizon: str = Field(min_length=2, max_length=100)
    context: str = Field(max_length=6000)

    @field_validator('organization', 'industry', 'challenge', 'horizon', 'context', mode='before')
    @classmethod
    def trim(cls, value):
        return value.strip() if isinstance(value, str) else value

class Evidence(StrictModel):
    id: str
    finding: str
    explanation: str
    category: Literal['Organization', 'Industry', 'Competition', 'Technology']
    source_title: str
    source_url: HttpUrl
    publication_date: str | None
    strength: Literal['High', 'Medium', 'Low']
    strength_reason: str
    relevance: str
    limitation: str

class Research(StrictModel):
    findings: list[Evidence] = Field(min_length=1, max_length=20)
    gaps: list[str]

DIMENSIONS = ('Stakeholder value', 'Business value', 'Technical feasibility',
              'Technology maturity', 'Implementation difficulty', 'Differentiation',
              'Evidence strength', 'Human impact', 'Risk', 'Time to implementation')

class Assessment(StrictModel):
    dimension: Literal['Stakeholder value', 'Business value', 'Technical feasibility',
                       'Technology maturity', 'Implementation difficulty', 'Differentiation',
                       'Evidence strength', 'Human impact', 'Risk', 'Time to implementation']
    rating: Literal['High', 'Medium', 'Low', 'Unknown']
    reason: str
    evidence_ids: list[str]

class Opportunity(StrictModel):
    id: str
    name: str
    problem_addressed: str
    technology: str
    how_it_works: str
    evidence_ids: list[str] = Field(min_length=1)
    business_value_hypothesis: str
    maturity: Literal['Academic research', 'Laboratory prototype', 'Demonstrated prototype',
                      'Pilot stage', 'Early commercialization', 'Commercially mature']
    maturity_reason: str
    competitive_implications: str
    barriers: list[str]
    time_horizon_estimate: str
    assessments: list[Assessment]

class Opportunities(StrictModel):
    opportunities: list[Opportunity] = Field(min_length=3, max_length=5)

class Phase(StrictModel):
    name: Literal['Validation', 'Prototype', 'Pilot', 'Evaluation', 'Scale Decision']
    actions: list[str]
    owner: str
    exit_gate: str
    duration_estimate: str

class KPI(StrictModel):
    name: str
    definition: str
    baseline_plan: str
    measurement_method: str
    decision_rule: str

class Roadmap(StrictModel):
    executive_summary: str
    strategic_objective: str
    why_it_matters: str
    evidence_ids: list[str] = Field(min_length=1)
    proposed_pilot: str
    required_capabilities: list[str]
    stakeholders: list[str]
    data_requirements: list[str]
    human_factors: list[str]
    technical_requirements: list[str]
    phases: list[Phase]
    kpis: list[KPI] = Field(min_length=2)
    assumptions: list[str]
    additional_research: list[str]
    feedback_response: str

class CritiqueItem(StrictModel):
    category: Literal['Unsupported claims', 'Weak evidence', 'Hallucination risks',
        'Assumptions', 'Missing stakeholders', 'Human factors', 'Data/privacy',
        'Ethics', 'Regulatory', 'Adoption', 'Alternative explanations',
        'Evidence needed', 'Failure modes']
    severity: Literal['High', 'Medium', 'Low']
    concern: str
    action: str
    evidence_ids: list[str]

class Critique(StrictModel):
    verdict: Literal['Revise before pilot', 'Conditional pilot candidate', 'Insufficient evidence']
    summary: str
    issues: list[CritiqueItem] = Field(min_length=3)
    strongest_counterargument: str
    nontechnology_alternative: str
