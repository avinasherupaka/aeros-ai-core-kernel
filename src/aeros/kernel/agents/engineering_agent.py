from __future__ import annotations

from aeros.kernel.agents.tools import AgentToolRegistry


class EngineeringAgent:
    persona = "engineering"

    def __init__(self, tools: AgentToolRegistry | None = None):
        self.tools = tools or AgentToolRegistry()

    def ask(self, question: str, event_id: str | None = None) -> dict:
        board = self.tools.get_engineering_reliability_board()
        resolved_event_id = self.tools.resolve_event_id(event_id)
        reliability = self.tools.get_similar_events(resolved_event_id)
        if "post-maintenance" in question.lower() or "recurrence" in question.lower():
            return {
                "persona": self.persona,
                "event_id": resolved_event_id,
                "answer": reliability["summary"],
                "classification": reliability["classification"],
                "maintenance_context": reliability["maintenance_context"],
            }
        if "recommended" in question.lower() or "actions" in question.lower():
            return {
                "persona": self.persona,
                "event_id": resolved_event_id,
                "answer": "Recommended engineering actions generated from recurrence context.",
                "recommended_actions": reliability["recommended_engineering_actions"],
            }
        return {
            "persona": self.persona,
            "answer": "Recurring hotspots are derived from the engineering reliability board.",
            "chronic_assets": board["chronic_assets"],
            "asset_recurrence_table": board["asset_recurrence_table"],
        }
