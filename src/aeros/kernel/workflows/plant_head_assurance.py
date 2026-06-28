from __future__ import annotations

from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.assurance.reliability_intelligence import ReliabilityInsight
from aeros.kernel.models.canonical import AssuranceEvent


class PlantHeadAssuranceView(BaseModel):
    site_id: str
    open_high_risk_events: list[str] = Field(default_factory=list)
    batch_release_risk_count: int = 0
    recurrence_hotspots: list[str] = Field(default_factory=list)
    action_priorities: list[str] = Field(default_factory=list)
    site_risk_score: float = 0.0
    site_risk_tier: str = ""
    executive_summary: str = ""


def build_plant_head_assurance_view(
    *,
    site_id: str,
    events: list[AssuranceEvent],
    impacts: list[ImpactAssessment],
    reliability_insights: list[ReliabilityInsight],
) -> PlantHeadAssuranceView:
    high_risk_events = [event.event_id for event in events if event.severity in {"high", "critical"}]
    batch_release_risk_count = sum(1 for impact in impacts if impact.impacted_batch_id and impact.likely_quality_risks)
    recurrence_hotspots = [insight.asset_id for insight in reliability_insights if insight.recurrence_count >= 1]
    action_priorities = [
        "Confirm high-risk events have human-approved evidence packs before disposition.",
        "Prioritize chronic recurrence hotspots for engineering review.",
        "Use Areos to connect events to validated state, product impact, and audit evidence; do not replace MES/QMS/SCADA systems of record.",
    ]
    
    total_events = max(len(events), 1)
    site_risk_score = min(1.0, (len(high_risk_events) * 2 + batch_release_risk_count + len(recurrence_hotspots)) / (total_events * 3))
    site_risk_score = round(site_risk_score, 2)
    
    if site_risk_score > 0.7:
        site_risk_tier = "critical"
    elif site_risk_score > 0.5:
        site_risk_tier = "high"
    elif site_risk_score > 0.3:
        site_risk_tier = "medium"
    else:
        site_risk_tier = "low"
    
    executive_summary = (
        f"Site {site_id} has {len(events)} events with {len(high_risk_events)} high-risk events. "
        f"{batch_release_risk_count} batch(es) at risk. {len(recurrence_hotspots)} asset(s) show recurrence. "
        f"Site risk tier: {site_risk_tier}. Action: review high-risk events and chronic recurrence assets."
    )
    
    return PlantHeadAssuranceView(
        site_id=site_id,
        open_high_risk_events=high_risk_events,
        batch_release_risk_count=batch_release_risk_count,
        recurrence_hotspots=sorted(set(recurrence_hotspots)),
        action_priorities=action_priorities,
        site_risk_score=site_risk_score,
        site_risk_tier=site_risk_tier,
        executive_summary=executive_summary,
    )
