"""Transitions enforce approval boundaries and remove stale downstream output."""
from dataclasses import dataclass, field
from schemas import Challenge, Research, Opportunities, Roadmap, Critique
from agents import WorkflowError

@dataclass
class Session:
    mode: str
    challenge: Challenge | None = None
    research: Research | None = None
    approved_ids: list[str] = field(default_factory=list)
    opportunities: Opportunities | None = None
    selected_ids: list[str] = field(default_factory=list)
    deep_id: str | None = None
    feedback: str = ''
    roadmap: Roadmap | None = None
    critique: Critique | None = None
    revision: int = 0

    @property
    def approved(self):
        return [e for e in self.research.findings if e.id in self.approved_ids] if self.research else []

    @property
    def selected(self):
        return [o for o in self.opportunities.opportunities if o.id in self.selected_ids] if self.opportunities else []

    def set_research(self, challenge, research):
        self.challenge, self.research = challenge, research
        self.approved_ids = []
        self.opportunities = None
        self.clear_strategy()
        self.revision += 1

    def clear_strategy(self):
        self.selected_ids, self.deep_id, self.feedback = [], None, ''
        self.roadmap = self.critique = None

    def approve(self, ids):
        if not self.research or not ids or not set(ids).issubset({e.id for e in self.research.findings}):
            raise WorkflowError('Include at least one valid evidence finding before continuing.')
        self.approved_ids = list(ids)
        self.opportunities = None
        self.clear_strategy()
        self.revision += 1

    def choose(self, ids, deep_id, feedback):
        if not self.opportunities or not ids or not set(ids).issubset({o.id for o in self.opportunities.opportunities}) or deep_id not in ids:
            raise WorkflowError('Select at least one opportunity and include your deep-dive choice.')
        self.selected_ids, self.deep_id, self.feedback = list(ids), deep_id, feedback.strip()
        self.roadmap = self.critique = None
