from __future__ import annotations

import re

from aeros.kernel.agents.tools import AgentToolRegistry


class QAAgent:
    persona = "qa"

    def __init__(self, tools: AgentToolRegistry | None = None):
        self.tools = tools or AgentToolRegistry()

    def ask(self, question: str, event_id: str | None = None) -> dict:
        batch_match = re.search(r"(BATCH-[A-Z0-9-]+)", question)
        resolved_event_id = self.tools.resolve_event_id(event_id, batch_id=batch_match.group(1) if batch_match else None)
        impact = self.tools.get_impact_assessment(resolved_event_id)
        dossier = self.tools.get_evidence_package(resolved_event_id)
        if "close" in question.lower() and "deviation" in question.lower():
            return {
                "persona": self.persona,
                "event_id": resolved_event_id,
                "answer": "No. Areos can prepare the evidence pack, but deviation closure requires human QA approval.",
                "human_approval_required": True,
                "missing_evidence": impact["missing_evidence"],
            }
        if "missing" in question.lower() and "evidence" in question.lower():
            return {
                "persona": self.persona,
                "event_id": resolved_event_id,
                "answer": f"Missing evidence for {resolved_event_id}: {', '.join(impact['missing_evidence']) or 'none'}.",
                "human_approval_required": True,
                "missing_evidence": impact["missing_evidence"],
                "package_completeness_score": dossier["package_completeness_score"],
            }
        batch_id = impact.get("impacted_batch_id") or "unknown batch"
        return {
            "persona": self.persona,
            "event_id": resolved_event_id,
            "answer": f"Batch {batch_id} was potentially impacted. Review quality risks, missing evidence, and obtain human QA approval before disposition.",
            "human_approval_required": True,
            "quality_risks": impact["likely_quality_risks"],
            "missing_evidence": impact["missing_evidence"],
        }
