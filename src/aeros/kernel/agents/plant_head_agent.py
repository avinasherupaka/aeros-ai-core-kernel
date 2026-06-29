from __future__ import annotations

from aeros.kernel.agents.tools import AgentToolRegistry


class PlantHeadAgent:
    persona = "plant_head"

    def __init__(self, tools: AgentToolRegistry | None = None):
        self.tools = tools or AgentToolRegistry()

    def ask(self, question: str, event_id: str | None = None) -> dict:
        assurance = self.tools.get_plant_head_assurance()
        if "release" in question.lower():
            return {
                "persona": self.persona,
                "answer": "Potential release impact exists when impacted batches require QA review and evidence is incomplete.",
                "batch_release_risk_count": assurance["batch_release_risk_count"],
                "open_high_risk_events": assurance["open_high_risk_events"],
            }
        if "top site risks" in question.lower() or "care about" in question.lower():
            return {
                "persona": self.persona,
                "answer": assurance["executive_summary"],
                "site_risk_tier": assurance["site_risk_tier"],
                "action_priorities": assurance["action_priorities"],
            }
        return {
            "persona": self.persona,
            "answer": assurance["executive_summary"],
            "site_risk_score": assurance["site_risk_score"],
            "open_high_risk_events": assurance["open_high_risk_events"],
        }
