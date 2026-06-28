from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"


class DataQuality(str, Enum):
    GOOD = "GOOD"
    UNCERTAIN = "UNCERTAIN"
    BAD = "BAD"
    SIMULATED = "SIMULATED"


class SourceLineage(BaseModel):
    tenant_id: str
    site_id: str
    source_system: str
    source_protocol: str
    connector_id: str
    trace_id: str
    source_timestamp: datetime
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality: DataQuality = DataQuality.GOOD
    source_record_reference: str


class EventTimeWindow(BaseModel):
    start_at: datetime
    end_at: datetime


class EventContext(BaseModel):
    area_id: str | None = None
    room_id: str | None = None
    asset_id: str | None = None
    utility_system_id: str | None = None
    batch_id: str | None = None
    product_id: str | None = None
    material_lot_id: str | None = None
    operation: str | None = None
    phase: str | None = None
    scenario_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RawSourceRecord(BaseModel):
    tenant_id: str
    site_id: str
    source_system: str
    source_protocol: str
    connector_id: str
    trace_id: str
    record_id: str
    record_type: str
    source_timestamp: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
    quality: DataQuality = DataQuality.GOOD


class CanonicalEvent(BaseModel):
    event_id: str
    tenant_id: str
    site_id: str
    event_type: str
    title: str
    description: str
    severity: EventSeverity = EventSeverity.MEDIUM
    status: EventStatus = EventStatus.OPEN
    parameter: str
    observed_value: float | None = None
    unit: str | None = None
    time_window: EventTimeWindow
    lineage: SourceLineage
    context: EventContext
    payload: dict[str, Any] = Field(default_factory=dict)


class AssuranceEvent(BaseModel):
    event_id: str
    canonical_event_id: str
    tenant_id: str
    site_id: str
    event_type: str
    severity: EventSeverity
    status: EventStatus = EventStatus.OPEN
    scenario_id: str | None = None
    risk_ids: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    confidence: float | None = None
    confidence_explanation: str | None = None
    lineage: SourceLineage
    context: EventContext
    payload: dict[str, Any] = Field(default_factory=dict)


def normalize_raw_source_record(
    raw_record: RawSourceRecord,
    *,
    event_id: str,
    title: str,
    description: str,
    parameter: str,
    observed_value: float | None,
    unit: str | None,
    event_type: str = "measurement",
    severity: EventSeverity = EventSeverity.MEDIUM,
    status: EventStatus = EventStatus.OPEN,
    context: EventContext | None = None,
) -> CanonicalEvent:
    time_window = EventTimeWindow(start_at=raw_record.source_timestamp, end_at=raw_record.source_timestamp)
    lineage = SourceLineage(
        tenant_id=raw_record.tenant_id,
        site_id=raw_record.site_id,
        source_system=raw_record.source_system,
        source_protocol=raw_record.source_protocol,
        connector_id=raw_record.connector_id,
        trace_id=raw_record.trace_id,
        source_timestamp=raw_record.source_timestamp,
        quality=raw_record.quality,
        source_record_reference=raw_record.record_id,
    )
    return CanonicalEvent(
        event_id=event_id,
        tenant_id=raw_record.tenant_id,
        site_id=raw_record.site_id,
        event_type=event_type,
        title=title,
        description=description,
        severity=severity,
        status=status,
        parameter=parameter,
        observed_value=observed_value,
        unit=unit,
        time_window=time_window,
        lineage=lineage,
        context=context or EventContext(),
        payload=raw_record.payload,
    )


def promote_to_assurance_event(
    canonical_event: CanonicalEvent,
    *,
    assurance_event_id: str,
    risk_ids: list[str] | None = None,
    required_evidence: list[str] | None = None,
    scenario_id: str | None = None,
    confidence: float | None = None,
    confidence_explanation: str | None = None,
) -> AssuranceEvent:
    return AssuranceEvent(
        event_id=assurance_event_id,
        canonical_event_id=canonical_event.event_id,
        tenant_id=canonical_event.tenant_id,
        site_id=canonical_event.site_id,
        event_type=canonical_event.event_type,
        severity=canonical_event.severity,
        status=canonical_event.status,
        scenario_id=scenario_id or canonical_event.context.scenario_id,
        risk_ids=risk_ids or [],
        required_evidence=required_evidence or [],
        confidence=confidence,
        confidence_explanation=confidence_explanation,
        lineage=canonical_event.lineage,
        context=canonical_event.context,
        payload=canonical_event.payload,
    )
