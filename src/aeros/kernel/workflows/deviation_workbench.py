from __future__ import annotations

from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.models.canonical import AssuranceEvent


class DeviationDraft(BaseModel):
    event_id: str
    deviation_title: str
    problem_statement: str
    impact_assessment_draft: str
    evidence_checklist: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    suggested_immediate_containment: list[str] = Field(default_factory=list)
    human_approval_required: bool = True
    approval_note: str = "QA human approval required before deviation closure."
    suggested_personas: list[str] = Field(default_factory=list)


class DeviationQueueItem(BaseModel):
    event_id: str
    site_id: str
    severity: str | None = None
    status: str = "triage_pending"
    owner: str | None = None
    impacted_batch_id: str | None = None
    missing_evidence_count: int = 0
    review_personas: list[str] = Field(default_factory=list)
    due_status: str = "open"


class DeviationWorkbenchView(BaseModel):
    queue: list[DeviationQueueItem] = Field(default_factory=list)


def create_deviation_draft(
    event: AssuranceEvent,
    impact: ImpactAssessment,
    dossier: "GMPDossier",
) -> DeviationDraft:
    containment = []
    if event.severity in ("critical", "high"):
        containment.append("Initiate batch hold for affected batches pending QA review.")
        containment.append("Notify QA manager and plant head immediately.")
    containment.append("Secure all relevant source records and ensure no data is overwritten.")
    containment.append("Confirm area/equipment status and ongoing production risk.")
    
    return DeviationDraft(
        event_id=event.event_id,
        deviation_title=f"Deviation: {event.metric} excursion at {event.site_id} ({event.severity or 'unknown'} severity)",
        problem_statement=(
            f"A {event.metric} event was detected at {event.site_id}, area {event.area_id}, "
            f"asset {event.asset_id}. Severity: {event.severity}. "
            f"Impacted batch: {impact.impacted_batch_id or 'TBD'}. "
            f"Impacted product: {impact.impacted_product_id or 'TBD'}."
        ),
        impact_assessment_draft=(
            f"Impacted area: {impact.impacted_area}. "
            f"Impacted batch: {impact.impacted_batch_id or 'n/a'}. "
            f"Impacted product: {impact.impacted_product_id or 'n/a'}. "
            f"Quality risks: {', '.join(impact.likely_quality_risks) or 'under assessment'}."
        ),
        evidence_checklist=impact.required_evidence,
        missing_evidence=impact.missing_evidence,
        suggested_immediate_containment=containment,
        human_approval_required=True,
        approval_note="QA human approval required before deviation closure.",
        suggested_personas=impact.suggested_human_review_owners,
    )


def build_deviation_queue(events: list[AssuranceEvent], impacts: list[ImpactAssessment]) -> DeviationWorkbenchView:
    impact_index = {impact.event_id: impact for impact in impacts}
    queue = [
        DeviationQueueItem(
            event_id=event.event_id,
            site_id=event.site_id,
            severity=event.severity,
            owner=(impact_index[event.event_id].suggested_human_review_owners[0] if impact_index[event.event_id].suggested_human_review_owners else None),
            impacted_batch_id=impact_index[event.event_id].impacted_batch_id,
            missing_evidence_count=len(impact_index[event.event_id].missing_evidence),
            review_personas=impact_index[event.event_id].suggested_human_review_owners,
            due_status="urgent" if event.severity in ("critical", "high") else "open",
        )
        for event in events
        if event.event_id in impact_index
    ]
    return DeviationWorkbenchView(queue=queue)
