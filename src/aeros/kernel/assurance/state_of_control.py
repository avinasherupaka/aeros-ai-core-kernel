"""
State-of-Control Engine for Areos.

Evaluates a stream of measurements against defined alert and action limits
to produce a StateOfControlAssessment.

This is the core Areos assurance capability:
  "Detect state-of-control breach → link to batch/product/room/equipment
   → preserve source lineage → prepare foundations for evidence dossiers."

AWS equivalent:
  AWS Lambda / Step Functions triggered by IoT Rules Engine.
  Inputs arrive from SiteWise property value history.
  Outputs stored in S3 evidence lake and DynamoDB canonical event store.

Usage:
    from aeros.kernel.storage.local_sitewise import MeasurementReading
    from aeros.kernel.assurance.state_of_control import run_humidity_state_of_control

    readings = [MeasurementReading(asset_id="ahu_03", measurement_name="relative_humidity",
                                   value=63.0, unit="%RH", ...)]
    assessment = run_humidity_state_of_control(readings, tenant_id="acme_pharma", ...)

Run tests:
    pytest tests/test_state_of_control.py
"""

import uuid
from datetime import datetime, timezone

from aeros.kernel.models.canonical import (
    AssessmentOutcome,
    AssuranceEvent,
    EventType,
    StateOfControlAssessment,
)
from aeros.kernel.storage.local_sitewise import MeasurementReading, classify_humidity_state


def run_humidity_state_of_control(
    readings: list[MeasurementReading],
    tenant_id: str,
    site_id: str,
    area_id: str,
    asset_id: str,
    alert_limit: float = 55.0,
    action_limit: float = 60.0,
    batch_id: str | None = None,
    product_id: str | None = None,
) -> StateOfControlAssessment:
    """
    Evaluate a relative-humidity reading stream against alert/action limits.

    Rules:
      - Any reading above action_limit → BREACH_CONFIRMED (if total > 0 minutes)
      - Any reading above alert_limit only → ALERT
      - All readings within limits → IN_CONTROL

    Returns a StateOfControlAssessment that includes:
      - outcome (IN_CONTROL / ALERT / ACTION_REQUIRED / BREACH_CONFIRMED)
      - excursion_duration_minutes (22.0 for the Dendrix demo)
      - breach start/end timestamps
      - peak value
      - full tenant/site/asset/batch lineage
    """
    if not readings:
        return StateOfControlAssessment(
            assessment_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            site_id=site_id,
            area_id=area_id,
            asset_id=asset_id,
            metric="relative_humidity",
            outcome=AssessmentOutcome.IN_CONTROL,
            excursion_duration_minutes=0.0,
            action_limit=action_limit,
            alert_limit=alert_limit,
            peak_value=0.0,
            batch_id=batch_id,
            product_id=product_id,
        )

    action_readings = [r for r in readings if r.value > action_limit]
    alert_only_readings = [r for r in readings if alert_limit < r.value <= action_limit]
    excursion_minutes = float(len(action_readings))
    peak_value = max(r.value for r in readings)
    breach_start = action_readings[0].timestamp if action_readings else None
    breach_end = action_readings[-1].timestamp if action_readings else None

    if excursion_minutes > 0:
        outcome = AssessmentOutcome.BREACH_CONFIRMED
    elif alert_only_readings:
        outcome = AssessmentOutcome.ALERT
    else:
        outcome = AssessmentOutcome.IN_CONTROL

    return StateOfControlAssessment(
        assessment_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        site_id=site_id,
        area_id=area_id,
        asset_id=asset_id,
        metric="relative_humidity",
        outcome=outcome,
        excursion_duration_minutes=excursion_minutes,
        breach_start=breach_start,
        breach_end=breach_end,
        action_limit=action_limit,
        alert_limit=alert_limit,
        peak_value=peak_value,
        batch_id=batch_id,
        product_id=product_id,
        source_lineage={
            "tenant_id": tenant_id,
            "site_id": site_id,
            "area_id": area_id,
            "asset_id": asset_id,
            "source_system": "bms_simulation",
            "metric": "relative_humidity",
        },
    )


def build_assurance_events_from_assessment(
    assessment: StateOfControlAssessment,
) -> list[AssuranceEvent]:
    """
    Convert a StateOfControlAssessment into one or more typed AssuranceEvents.

    A BREACH_CONFIRMED assessment produces a STATE_OF_CONTROL_BREACH event.
    These events are the input to the Event Router and downstream evidence builders.
    """
    events: list[AssuranceEvent] = []

    if assessment.outcome == AssessmentOutcome.BREACH_CONFIRMED:
        events.append(
            AssuranceEvent(
                event_id=str(uuid.uuid4()),
                tenant_id=assessment.tenant_id,
                site_id=assessment.site_id,
                area_id=assessment.area_id,
                event_type=EventType.STATE_OF_CONTROL_BREACH,
                source_system="state_of_control_engine",
                asset_id=assessment.asset_id,
                metric=assessment.metric,
                timestamp=assessment.assessed_at,
                value=assessment.peak_value,
                unit="%RH",
                batch_id=assessment.batch_id,
                product_id=assessment.product_id,
                payload={
                    "excursion_duration_minutes": assessment.excursion_duration_minutes,
                    "breach_start": assessment.breach_start.isoformat() if assessment.breach_start else None,
                    "breach_end": assessment.breach_end.isoformat() if assessment.breach_end else None,
                    "action_limit": assessment.action_limit,
                    "alert_limit": assessment.alert_limit,
                    "assessment_id": assessment.assessment_id,
                    "source_lineage": assessment.source_lineage,
                },
                trace_id=assessment.assessment_id,
            )
        )
    elif assessment.outcome == AssessmentOutcome.ALERT:
        events.append(
            AssuranceEvent(
                event_id=str(uuid.uuid4()),
                tenant_id=assessment.tenant_id,
                site_id=assessment.site_id,
                area_id=assessment.area_id,
                event_type=EventType.ALERT_TRIGGERED,
                source_system="state_of_control_engine",
                asset_id=assessment.asset_id,
                metric=assessment.metric,
                timestamp=assessment.assessed_at,
                value=assessment.peak_value,
                unit="%RH",
                batch_id=assessment.batch_id,
                product_id=assessment.product_id,
                payload={"alert_limit": assessment.alert_limit},
                trace_id=assessment.assessment_id,
            )
        )

    return events
