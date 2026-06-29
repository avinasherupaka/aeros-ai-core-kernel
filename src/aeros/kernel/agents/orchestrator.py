from __future__ import annotations

from aeros.kernel.agents.engineering_agent import EngineeringAgent
from aeros.kernel.agents.plant_head_agent import PlantHeadAgent
from aeros.kernel.agents.qa_agent import QAAgent
from aeros.kernel.agents.validation_agent import ValidationAgent


class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "qa": QAAgent(),
            "engineering": EngineeringAgent(),
            "plant_head": PlantHeadAgent(),
            "validation": ValidationAgent(),
        }

    def classify_persona(self, question: str, persona: str | None = None) -> str:
        if persona in self.agents:
            return persona
        lowered = question.lower()
        if any(token in lowered for token in ["deviation", "evidence", "batch"]):
            return "qa"
        if any(token in lowered for token in ["maintenance", "hotspot", "engineering", "recurrence"]):
            return "engineering"
        if any(token in lowered for token in ["audit", "validation", "lineage", "compliance"]):
            return "validation"
        return "plant_head"

    def ask(self, question: str, *, persona: str | None = None, event_id: str | None = None) -> dict:
        selected = self.classify_persona(question, persona)
        response = self.agents[selected].ask(question, event_id=event_id)
        response["routed_persona"] = selected
        return response
