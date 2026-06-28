from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, Field

from aeros.kernel.assurance.reliability_intelligence import ReliabilityInsight
from aeros.kernel.models.canonical import AssuranceEvent


class EngineeringReliabilityBoard(BaseModel):
    site_id: str
    asset_event_counts: dict[str, int] = Field(default_factory=dict)
    chronic_assets: list[str] = Field(default_factory=list)
    recent_maintenance_context: list[str] = Field(default_factory=list)
    suggested_review_topics: list[str] = Field(default_factory=list)
    suggested_engineering_actions: list[str] = Field(default_factory=list)
    maintenance_effectiveness_flags: list[str] = Field(default_factory=list)
    asset_recurrence_table: list[dict] = Field(default_factory=list)


def build_engineering_reliability_board(
    *,
    site_id: str,
    events: list[AssuranceEvent],
    reliability_insights: list[ReliabilityInsight],
) -> EngineeringReliabilityBoard:
    counts = Counter(event.asset_id for event in events)
    chronic_assets = [insight.asset_id for insight in reliability_insights if insight.classification.value in {"chronic_recurrence", "post_maintenance_recurrence"}]
    maintenance_context = [insight.maintenance_context for insight in reliability_insights if insight.maintenance_context]
    topics = []
    if chronic_assets:
        topics.append("Review chronic recurrence assets and confirm root-cause/corrective actions.")
    if maintenance_context:
        topics.append("Verify whether recent maintenance was effective for post-maintenance recurrences.")
    if not topics:
        topics.append("No chronic reliability hotspots detected in the current demo dataset.")
    
    suggested_engineering_actions = []
    for insight in reliability_insights:
        suggested_engineering_actions.extend(insight.recommended_engineering_actions)
    suggested_engineering_actions = list(dict.fromkeys(suggested_engineering_actions))
    
    maintenance_effectiveness_flags = []
    for insight in reliability_insights:
        if insight.classification.value == "post_maintenance_recurrence":
            maintenance_effectiveness_flags.append(
                f"Asset {insight.asset_id}: recurrence after maintenance (WO: {insight.maintenance_context or 'unknown'})"
            )
    
    asset_recurrence_table = [
        {
            "asset_id": insight.asset_id,
            "metric": insight.metric,
            "recurrence_count": insight.recurrence_count,
            "classification": insight.classification.value,
        }
        for insight in reliability_insights
    ]
    
    return EngineeringReliabilityBoard(
        site_id=site_id,
        asset_event_counts=dict(counts),
        chronic_assets=sorted(set(chronic_assets)),
        recent_maintenance_context=maintenance_context,
        suggested_review_topics=topics,
        suggested_engineering_actions=suggested_engineering_actions,
        maintenance_effectiveness_flags=maintenance_effectiveness_flags,
        asset_recurrence_table=asset_recurrence_table,
    )
