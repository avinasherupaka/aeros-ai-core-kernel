from __future__ import annotations

from aeros.kernel.agents.tools import AgentToolRegistry


class ValidationAgent:
    persona = "validation"

    def __init__(self, tools: AgentToolRegistry | None = None):
        self.tools = tools or AgentToolRegistry()

    def ask(self, question: str, event_id: str | None = None) -> dict:
        room = self.tools.get_validation_audit_room()
        resolved_event_id = self.tools.resolve_event_id(event_id)
        if "lineage" in question.lower() or "incomplete" in question.lower():
            return {
                "persona": self.persona,
                "event_id": resolved_event_id,
                "answer": "Evidence lineage is incomplete where required source records are still missing.",
                "missing_source_records": room["missing_source_records"].get(resolved_event_id, []),
            }
        if "compliance" in question.lower() or "notes" in question.lower():
            return {
                "persona": self.persona,
                "answer": "Validation/compliance notes are advisory and human-reviewed.",
                "validation_notes": room["validation_notes"],
            }
        return {
            "persona": self.persona,
            "event_id": resolved_event_id,
            "answer": f"Audit readiness for {resolved_event_id}: {room['audit_ready_status'].get(resolved_event_id, 'unknown')}.",
            "audit_ready_status": room["audit_ready_status"].get(resolved_event_id, "unknown"),
            "approval_status": room["approval_status"].get(resolved_event_id, "unknown"),
        }
