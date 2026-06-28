from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum

from pydantic import BaseModel, Field

from aeros.kernel.models.canonical import AssuranceEvent


class RecurrenceClassification(str, Enum):
    FIRST_OCCURRENCE = "first_occurrence"
    REPEATED_EVENT = "repeated_event"
    CHRONIC_RECURRENCE = "chronic_recurrence"
    POST_MAINTENANCE_RECURRENCE = "post_maintenance_recurrence"
    SEASONAL_OR_SHIFT_PATTERN_SUSPECTED = "seasonal_or_shift_pattern_suspected"


class MaintenanceRecord(BaseModel):
    work_order_id: str
    asset_id: str
    completed_at: datetime
    summary: str


class ReliabilityInsight(BaseModel):
    event_id: str
    asset_id: str
    metric: str
    lookback_days: int
    recurrence_count: int
    similar_event_ids: list[str] = Field(default_factory=list)
    classification: RecurrenceClassification
    maintenance_context: str | None = None
    summary: str
    similarity_score: float = 0.0
    recommended_engineering_actions: list[str] = Field(default_factory=list)
    recurrence_by_asset_metric: dict[str, int] = Field(default_factory=dict)


def analyze_recurrence(
    anchor_event: AssuranceEvent,
    prior_events: list[AssuranceEvent],
    *,
    lookback_days: int = 30,
    maintenance_records: list[MaintenanceRecord] | None = None,
) -> ReliabilityInsight:
    maintenance_records = maintenance_records or []
    anchor_time = anchor_event.timestamp if anchor_event.timestamp.tzinfo else anchor_event.timestamp.replace(tzinfo=timezone.utc)
    window_start = anchor_time - timedelta(days=lookback_days)
    similar_events = [
        event
        for event in prior_events
        if event.site_id == anchor_event.site_id
        and event.asset_id == anchor_event.asset_id
        and event.metric == anchor_event.metric
        and window_start <= (event.timestamp if event.timestamp.tzinfo else event.timestamp.replace(tzinfo=timezone.utc)) <= anchor_time
    ]
    maintenance_match = next(
        (
            record
            for record in maintenance_records
            if record.asset_id == anchor_event.asset_id and record.completed_at <= anchor_time and record.completed_at >= window_start
        ),
        None,
    )
    recurrence_count = len(similar_events)
    if maintenance_match and recurrence_count >= 1:
        classification = RecurrenceClassification.POST_MAINTENANCE_RECURRENCE
    elif recurrence_count >= 3:
        classification = RecurrenceClassification.CHRONIC_RECURRENCE
    elif recurrence_count >= 1:
        classification = RecurrenceClassification.REPEATED_EVENT
    else:
        classification = RecurrenceClassification.FIRST_OCCURRENCE

    maintenance_context = None
    if maintenance_match:
        maintenance_context = f"{maintenance_match.work_order_id}: {maintenance_match.summary}"

    summary = {
        RecurrenceClassification.FIRST_OCCURRENCE: "First occurrence in the configured lookback window.",
        RecurrenceClassification.REPEATED_EVENT: "Repeated event detected on the same site/asset/parameter.",
        RecurrenceClassification.CHRONIC_RECURRENCE: "Chronic recurrence detected; asset should be reviewed by engineering reliability board.",
        RecurrenceClassification.POST_MAINTENANCE_RECURRENCE: "Event recurred after recent maintenance and should be reviewed for maintenance effectiveness.",
        RecurrenceClassification.SEASONAL_OR_SHIFT_PATTERN_SUSPECTED: "Seasonal or shift pattern suspected.",
    }[classification]

    similarity_score = 0.0
    if similar_events:
        similarity_score = 0.7
        if any(e.product_id == anchor_event.product_id for e in similar_events):
            similarity_score += 0.1
        if any(e.area_id == anchor_event.area_id for e in similar_events):
            similarity_score += 0.1
        similarity_score = round(min(1.0, similarity_score), 2)

    recommended_engineering_actions = []
    if classification == RecurrenceClassification.FIRST_OCCURRENCE:
        recommended_engineering_actions = [
            "Monitor for recurrence over the next 30 days.",
            "Confirm source-system data quality and completeness.",
        ]
    elif classification == RecurrenceClassification.REPEATED_EVENT:
        recommended_engineering_actions = [
            "Investigate root cause of repeat events on this asset.",
            "Check maintenance schedule and preventive actions.",
            "Review BMS/EMS alarm settings.",
        ]
    elif classification == RecurrenceClassification.CHRONIC_RECURRENCE:
        recommended_engineering_actions = [
            "Escalate to engineering reliability board.",
            "Consider asset replacement or major overhaul.",
            "Root-cause analysis mandatory before CAPA closure.",
            "Review design adequacy of HVAC/utility system.",
        ]
    elif classification == RecurrenceClassification.POST_MAINTENANCE_RECURRENCE:
        recommended_engineering_actions = [
            "Assess maintenance effectiveness; work order may not have addressed root cause.",
            "Check if correct maintenance procedure was followed.",
            "Consider additional engineering controls.",
        ]
    elif classification == RecurrenceClassification.SEASONAL_OR_SHIFT_PATTERN_SUSPECTED:
        recommended_engineering_actions = [
            "Analyze event timestamps for seasonal or shift patterns.",
            "Review HVAC seasonal setpoints.",
            "Consider environmental monitoring trending.",
        ]

    recurrence_by_asset_metric = {f"{anchor_event.asset_id}::{anchor_event.metric}": recurrence_count}

    return ReliabilityInsight(
        event_id=anchor_event.event_id,
        asset_id=anchor_event.asset_id,
        metric=anchor_event.metric,
        lookback_days=lookback_days,
        recurrence_count=recurrence_count,
        similar_event_ids=[event.event_id for event in similar_events],
        classification=classification,
        maintenance_context=maintenance_context,
        summary=summary,
        similarity_score=similarity_score,
        recommended_engineering_actions=recommended_engineering_actions,
        recurrence_by_asset_metric=recurrence_by_asset_metric,
    )
