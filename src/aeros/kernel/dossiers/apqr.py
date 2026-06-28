from __future__ import annotations

from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.assurance.reliability_intelligence import ReliabilityInsight
from aeros.kernel.models.canonical import AssuranceEvent


class APQRSection(BaseModel):
    site_id: str
    utility_environmental_events: list[str] = Field(default_factory=list)
    recurrence_summary: list[str] = Field(default_factory=list)
    product_batch_risk_context: list[str] = Field(default_factory=list)
    capa_deviation_placeholders: list[str] = Field(default_factory=list)
    management_review_recommendations: list[str] = Field(default_factory=list)


def build_apqr_section(
    *,
    site_id: str,
    events: list[AssuranceEvent],
    impacts: list[ImpactAssessment],
    reliability_insights: list[ReliabilityInsight],
) -> APQRSection:
    utility_environmental_events = [
        f"{event.metric} / {event.event_type.value} / severity={event.severity or 'unknown'}"
        for event in events
    ]
    recurrence_summary = [
        f"{insight.asset_id}: {insight.classification.value} ({insight.recurrence_count} prior similar events)"
        for insight in reliability_insights
    ]
    product_batch_risk_context = [
        f"event={impact.event_id} batch={impact.impacted_batch_id or 'n/a'} product={impact.impacted_product_id or 'n/a'} risks={', '.join(impact.likely_quality_risks)}"
        for impact in impacts
    ]
    capa_deviation_placeholders = [
        f"Deviation placeholder for {impact.event_id}; CAPA to be human-approved if risk persists."
        for impact in impacts
    ]
    management_review_recommendations = [
        "Review recurrence hotspots and chronic assets with engineering reliability board.",
        "Confirm that missing evidence items are completed before APQR closure.",
        "Use Areos as proof linkage across existing systems; do not reposition it as a system of record.",
    ]
    return APQRSection(
        site_id=site_id,
        utility_environmental_events=utility_environmental_events,
        recurrence_summary=recurrence_summary,
        product_batch_risk_context=product_batch_risk_context,
        capa_deviation_placeholders=capa_deviation_placeholders,
        management_review_recommendations=management_review_recommendations,
    )
