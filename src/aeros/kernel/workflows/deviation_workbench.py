from __future__ import annotations

from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.models.canonical import AssuranceEvent


class DeviationQueueItem(BaseModel):
    event_id: str
    site_id: str
    severity: str | None = None
    status: str = "triage_pending"
    owner: str | None = None
    impacted_batch_id: str | None = None
    missing_evidence_count: int = 0
    review_personas: list[str] = Field(default_factory=list)


class DeviationWorkbenchView(BaseModel):
    queue: list[DeviationQueueItem] = Field(default_factory=list)


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
        )
        for event in events
        if event.event_id in impact_index
    ]
    return DeviationWorkbenchView(queue=queue)
