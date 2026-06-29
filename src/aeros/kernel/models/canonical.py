"""
Canonical event and assurance assessment models for Areos.

These are the normalized output types that flow from the ingestion/assurance
layer into evidence storage, APQR workflows, and deviation assessments.

Key types:
  CanonicalEvent            — generic normalized measurement event
  AssuranceEvent            — typed assurance event (STATE_OF_CONTROL_BREACH, etc.)
  StateOfControlAssessment  — result of running the state-of-control engine

AWS equivalent:
  Lambda/Step Functions produce these structured outputs, stored in S3/DynamoDB
  as the canonical event log and evidence record.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    MEASUREMENT = "measurement"
    STATE_OF_CONTROL_BREACH = "state_of_control_breach"
    STATE_RESTORED = "state_restored"
    ALERT_TRIGGERED = "alert_triggered"
    ACTION_REQUIRED = "action_required"
    BATCH_EVENT = "batch_event"
    UTILITY_ANOMALY = "utility_anomaly"


class AssessmentOutcome(str, Enum):
    IN_CONTROL = "IN_CONTROL"
    ALERT = "ALERT"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    BREACH_CONFIRMED = "BREACH_CONFIRMED"


class CanonicalEvent(BaseModel):
    """Generic normalized event — wraps any raw source payload."""

    event_id: str | None = None
    tenant_id: str
    site_id: str
    event_type: str
    source_system: str
    source_protocol: str | None = None
    connector_id: str | None = None
    trace_id: str | None = None
    source_timestamp: datetime | None = None
    ingestion_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality: str = "GOOD"
    source_record_reference: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)


class AssuranceEvent(BaseModel):
    """
    Typed assurance event emitted by the state-of-control engine or event router.
    Carries full tenant/site/asset lineage so evidence records can be traced back
    to source.
    """

    event_id: str
    tenant_id: str
    site_id: str
    area_id: str
    event_type: EventType
    source_system: str
    asset_id: str
    metric: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    value: float | None = None
    unit: str | None = None
    batch_id: str | None = None
    product_id: str | None = None
    room_id: str | None = None
    material_lot_id: str | None = None
    operation: str | None = None
    phase: str | None = None
    source_protocol: str | None = None
    connector_id: str | None = None
    quality: str = "GOOD"
    severity: str | None = None
    status: str | None = None
    risk_ids: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None


class StateOfControlAssessment(BaseModel):
    """
    Result of evaluating a stream of measurements against alert/action limits.

    A BREACH_CONFIRMED outcome with excursion_duration_minutes > 0 is the
    trigger for an Areos evidence dossier, deviation assessment, and APQR entry.

    Source lineage is preserved so QA can trace back to the original
    BMS/EMS tag and UNS topic.
    """

    assessment_id: str
    tenant_id: str
    site_id: str
    area_id: str
    asset_id: str
    metric: str
    outcome: AssessmentOutcome
    excursion_duration_minutes: float
    breach_start: datetime | None = None
    breach_end: datetime | None = None
    action_limit: float | None = None
    alert_limit: float | None = None
    critical_limit: float | None = None
    validated_range: dict[str, float | None] | None = None
    peak_value: float
    batch_id: str | None = None
    product_id: str | None = None
    room_id: str | None = None
    material_lot_id: str | None = None
    operation: str | None = None
    phase: str | None = None
    severity: str | None = None
    confidence: float | None = None
    confidence_explanation: str | None = None
    scenario_id: str | None = None
    duration_window_minutes: int | None = None
    parameter_assessments: list[dict[str, Any]] = Field(default_factory=list)
    source_lineage: dict[str, Any] = Field(default_factory=dict)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_breakdown: dict[str, Any] = Field(default_factory=dict)
