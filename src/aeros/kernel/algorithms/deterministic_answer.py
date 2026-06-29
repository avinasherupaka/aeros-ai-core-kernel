"""
Deterministic structured answer object.

Answers are produced from deterministic data objects, not LLM output.
Bedrock may render/explain these answers but must not modify their factual basis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AnswerType(str, Enum):
    QA_IMPACT = "qa_impact"
    AUDIT_READINESS = "audit_readiness"
    ENGINEERING_RELIABILITY = "engineering_reliability"
    PLANT_HEAD_RISK = "plant_head_risk"
    DEVIATION_DRAFT = "deviation_draft"


class DecisionState(str, Enum):
    CONFIRMED_IN_CONTROL = "confirmed_in_control"
    CONFIRMED_OUT_OF_CONTROL = "confirmed_out_of_control"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    HUMAN_APPROVED = "human_approved"
    HUMAN_REJECTED = "human_rejected"


@dataclass(frozen=True)
class AnswerCitation:
    source_system: str
    record_id: str
    record_type: str
    timestamp: str
    excerpt: str = ""


@dataclass
class DeterministicAnswer:
    answer_id: str
    answer_type: AnswerType
    answer_text: str
    decision_state: DecisionState
    basis_facts: list[str] = field(default_factory=list)
    citations: list[AnswerCitation] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    human_review_required: bool = True
    generated_from_versions: dict[str, str] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_complete(self) -> bool:
        return len(self.missing_evidence) == 0

    def requires_human_approval(self) -> bool:
        return self.human_review_required or self.decision_state == DecisionState.PENDING_HUMAN_REVIEW


def compose_qa_impact_answer(
    *,
    answer_id: str,
    event_summary: str,
    impacted_batches: list[str],
    quality_risks: list[str],
    evidence_status: str,
    missing_evidence: list[str],
    citations: list[AnswerCitation],
    versions: dict[str, str],
) -> DeterministicAnswer:
    impact_text = ", ".join(impacted_batches) if impacted_batches else "no active batches identified"
    risks_text = "; ".join(quality_risks) if quality_risks else "no quality risks identified"
    answer_text = (
        f"Event: {event_summary}. "
        f"Impacted batches: {impact_text}. "
        f"Quality risks: {risks_text}. "
        f"Evidence status: {evidence_status}. "
        f"This answer was produced deterministically from operational and quality data. "
        f"Human review and approval required for any GxP decision."
    )
    decision_state = (
        DecisionState.PENDING_HUMAN_REVIEW
        if missing_evidence
        else DecisionState.CONFIRMED_OUT_OF_CONTROL
    )
    return DeterministicAnswer(
        answer_id=answer_id,
        answer_type=AnswerType.QA_IMPACT,
        answer_text=answer_text,
        decision_state=decision_state,
        basis_facts=[event_summary, f"Impacted batches: {impact_text}", f"Risks: {risks_text}"],
        citations=citations,
        missing_evidence=missing_evidence,
        human_review_required=True,
        generated_from_versions=versions,
    )


def compose_audit_readiness_answer(
    *,
    answer_id: str,
    event_id: str,
    dossier_completeness_score: float,
    missing_evidence: list[str],
    citations: list[AnswerCitation],
    versions: dict[str, str],
) -> DeterministicAnswer:
    ready = dossier_completeness_score >= 1.0 and not missing_evidence
    answer_text = (
        f"Event {event_id}: dossier completeness {dossier_completeness_score:.0%}. "
        + (
            "Evidence package is audit-ready pending human approval."
            if ready
            else f"Missing evidence items: {', '.join(missing_evidence)}. Package NOT audit-ready."
        )
    )
    return DeterministicAnswer(
        answer_id=answer_id,
        answer_type=AnswerType.AUDIT_READINESS,
        answer_text=answer_text,
        decision_state=DecisionState.PENDING_HUMAN_REVIEW if not ready else DecisionState.PENDING_HUMAN_REVIEW,
        basis_facts=[f"Completeness: {dossier_completeness_score:.0%}", f"Missing: {missing_evidence}"],
        citations=citations,
        missing_evidence=missing_evidence,
        human_review_required=True,
        generated_from_versions=versions,
    )


def compose_engineering_reliability_answer(
    *,
    answer_id: str,
    asset_id: str,
    recurrence_count: int,
    recurrence_classification: str,
    recommended_actions: list[str],
    citations: list[AnswerCitation],
    versions: dict[str, str],
) -> DeterministicAnswer:
    actions_text = "; ".join(recommended_actions) if recommended_actions else "no immediate actions required"
    answer_text = (
        f"Asset {asset_id}: {recurrence_count} recurrences classified as '{recurrence_classification}'. "
        f"Recommended actions: {actions_text}. "
        f"Engineering review required."
    )
    return DeterministicAnswer(
        answer_id=answer_id,
        answer_type=AnswerType.ENGINEERING_RELIABILITY,
        answer_text=answer_text,
        decision_state=DecisionState.PENDING_HUMAN_REVIEW,
        basis_facts=[f"Recurrence count: {recurrence_count}", f"Classification: {recurrence_classification}"],
        citations=citations,
        missing_evidence=[],
        human_review_required=True,
        generated_from_versions=versions,
    )
