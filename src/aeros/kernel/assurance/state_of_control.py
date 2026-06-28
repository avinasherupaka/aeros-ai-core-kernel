"""
State-of-Control Engine for Areos.

Evaluates measurement streams against validated, alert, action, and critical
limits to produce a StateOfControlAssessment.

This is the core Areos assurance capability:
  "Do not sell monitoring; sell proof. Existing systems monitor signals; Areos
   connects signals to validated state, product impact, and audit evidence."

AWS equivalent:
  AWS Lambda / Step Functions triggered by IoT Rules Engine.
  Inputs arrive from SiteWise property value history.
  Outputs stored in S3 evidence lake and DynamoDB canonical event store.

Run tests:
    pytest tests/test_state_of_control.py tests/test_state_of_control_engine.py
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, Field

from aeros.kernel.models.canonical import (
    AssessmentOutcome,
    AssuranceEvent,
    EventType,
    StateOfControlAssessment,
)
from aeros.kernel.ontology.industry_packs import ScenarioDefinition
from aeros.kernel.storage.local_sitewise import MeasurementReading


class LimitBand(BaseModel):
    min_value: float | None = None
    max_value: float | None = None


class ParameterLimits(BaseModel):
    parameter: str
    unit: str
    validated_range: LimitBand | None = None
    alert_limit: LimitBand | None = None
    action_limit: LimitBand | None = None
    critical_limit: LimitBand | None = None
    duration_window_minutes: int = 1


class ParameterObservation(BaseModel):
    parameter: str
    value: float
    unit: str
    timestamp: datetime
    quality: str = "GOOD"
    source_system: str = ""


class ParameterAssessment(BaseModel):
    parameter: str
    unit: str
    observed_min: float
    observed_max: float
    peak_value: float
    breach_duration_minutes: float = 0.0
    alert_duration_minutes: float = 0.0
    critical_duration_minutes: float = 0.0
    severity: str = "info"
    outcome: AssessmentOutcome = AssessmentOutcome.IN_CONTROL
    confidence: float = 1.0
    confidence_explanation: str = "All source records reported GOOD quality."
    limit_summary: dict[str, Any] = Field(default_factory=dict)
    first_breach_timestamp: datetime | None = None
    last_breach_timestamp: datetime | None = None
    total_breach_minutes: float = 0.0
    longest_continuous_breach_minutes: float = 0.0
    evidence_references: list[str] = Field(default_factory=list)
    confidence_breakdown: dict[str, Any] = Field(default_factory=dict)


def _to_limit_band(raw: dict[str, float] | None) -> LimitBand | None:
    if raw is None:
        return None
    return LimitBand(min_value=raw.get("min"), max_value=raw.get("max"))


def build_state_of_control_rules_from_scenario(scenario: ScenarioDefinition) -> list[ParameterLimits]:
    return [
        ParameterLimits(
            parameter=parameter,
            unit=config.unit,
            validated_range=_to_limit_band(config.validated_range),
            alert_limit=_to_limit_band(config.alert_limit),
            action_limit=_to_limit_band(config.action_limit),
            critical_limit=_to_limit_band(config.critical_limit),
            duration_window_minutes=max((trigger.duration_minutes for trigger in scenario.demo_triggers if trigger.parameter == parameter), default=1),
        )
        for parameter, config in scenario.sample_limits.items()
    ]


def _baseline_value(limits: ParameterLimits) -> float:
    if limits.validated_range and limits.validated_range.min_value is not None and limits.validated_range.max_value is not None:
        return round((limits.validated_range.min_value + limits.validated_range.max_value) / 2, 3)
    if limits.validated_range and limits.validated_range.max_value is not None:
        return round(max(limits.validated_range.max_value - 1.0, 0.0), 3)
    if limits.validated_range and limits.validated_range.min_value is not None:
        return round(limits.validated_range.min_value + 1.0, 3)
    if limits.action_limit and limits.action_limit.max_value is not None:
        return round(limits.action_limit.max_value - 1.0, 3)
    if limits.action_limit and limits.action_limit.min_value is not None:
        return round(limits.action_limit.min_value + 1.0, 3)
    return 0.0


def build_demo_observations_from_scenario(
    scenario: ScenarioDefinition,
    *,
    start_time: datetime | None = None,
) -> list[ParameterObservation]:
    rules = {rule.parameter: rule for rule in build_state_of_control_rules_from_scenario(scenario)}
    base_time = start_time or datetime.now(timezone.utc).replace(microsecond=0)
    observations: list[ParameterObservation] = []
    for trigger in scenario.demo_triggers:
        limits = rules[trigger.parameter]
        baseline = _baseline_value(limits)
        for minute in range(3):
            observations.append(
                ParameterObservation(
                    parameter=trigger.parameter,
                    value=baseline,
                    unit=limits.unit,
                    timestamp=base_time + timedelta(minutes=minute),
                    quality=trigger.quality,
                    source_system=scenario.source_systems[0] if scenario.source_systems else "demo",
                )
            )
        for minute in range(trigger.duration_minutes):
            observations.append(
                ParameterObservation(
                    parameter=trigger.parameter,
                    value=trigger.breach_value,
                    unit=limits.unit,
                    timestamp=base_time + timedelta(minutes=3 + minute),
                    quality=trigger.quality,
                    source_system=scenario.source_systems[0] if scenario.source_systems else "demo",
                )
            )
    observations.sort(key=lambda item: item.timestamp)
    return observations


def _outside_band(value: float, band: LimitBand | None) -> bool:
    if band is None:
        return False
    if band.min_value is not None and value < band.min_value:
        return True
    if band.max_value is not None and value > band.max_value:
        return True
    return False


def _severity_rank(severity: str) -> int:
    return {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}.get(severity, 0)


def _extract_limit_value(limit_band: LimitBand | None) -> float | None:
    if limit_band is None:
        return None
    if limit_band.max_value is not None:
        return limit_band.max_value
    return limit_band.min_value


def _quality_confidence(qualities: list[str]) -> tuple[float, str]:
    normalized = {quality.upper() for quality in qualities} or {"GOOD"}
    if "BAD" in normalized:
        return 0.45, "At least one source record reported BAD quality; human review required."
    if "UNCERTAIN" in normalized or "SIMULATED" in normalized:
        return 0.7, "Source quality includes UNCERTAIN or SIMULATED data; confidence reduced."
    return 0.95, "All source records reported GOOD quality."


def _evaluate_parameter(observations: list[ParameterObservation], limits: ParameterLimits) -> ParameterAssessment:
    values = [observation.value for observation in observations]
    action_hits = [observation for observation in observations if _outside_band(observation.value, limits.action_limit)]
    alert_hits = [observation for observation in observations if _outside_band(observation.value, limits.alert_limit)]
    critical_hits = [observation for observation in observations if _outside_band(observation.value, limits.critical_limit)]
    confidence, confidence_explanation = _quality_confidence([observation.quality for observation in observations])

    if critical_hits:
        severity = "critical"
        outcome = AssessmentOutcome.BREACH_CONFIRMED
    elif len(action_hits) >= limits.duration_window_minutes:
        severity = "high"
        outcome = AssessmentOutcome.BREACH_CONFIRMED
    elif action_hits:
        severity = "high"
        outcome = AssessmentOutcome.ACTION_REQUIRED
    elif alert_hits:
        severity = "medium"
        outcome = AssessmentOutcome.ALERT
    else:
        severity = "info"
        outcome = AssessmentOutcome.IN_CONTROL

    first_breach_timestamp = action_hits[0].timestamp if action_hits else None
    last_breach_timestamp = action_hits[-1].timestamp if action_hits else None
    total_breach_minutes = float(len(action_hits))
    
    longest_continuous_breach_minutes = 0.0
    if action_hits:
        current_streak = 1
        max_streak = 1
        for i in range(1, len(action_hits)):
            time_diff = (action_hits[i].timestamp - action_hits[i-1].timestamp).total_seconds() / 60
            if time_diff <= 1.0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        longest_continuous_breach_minutes = float(max_streak)
    
    evidence_references = [
        f"{obs.source_system}:{obs.timestamp.isoformat()}" 
        for obs in action_hits[:3]
    ]
    
    qualities = [observation.quality for observation in observations]
    normalized_qualities = {q.upper() for q in qualities} or {"GOOD"}
    if "BAD" in normalized_qualities:
        source_quality = 0.45
    elif "UNCERTAIN" in normalized_qualities or "SIMULATED" in normalized_qualities:
        source_quality = 0.7
    else:
        source_quality = 1.0
    
    completeness = min(1.0, len(observations) / 5)
    
    time_window_continuity = 1.0
    if len(observations) > 1:
        for i in range(1, len(observations)):
            time_diff = (observations[i].timestamp - observations[i-1].timestamp).total_seconds() / 60
            if time_diff > 1.0:
                time_window_continuity = 0.8
                break
    
    confidence_breakdown = {
        "source_quality": source_quality,
        "completeness": completeness,
        "time_window_continuity": time_window_continuity,
        "context_present": False,
    }

    return ParameterAssessment(
        parameter=limits.parameter,
        unit=limits.unit,
        observed_min=min(values),
        observed_max=max(values),
        peak_value=max(values, key=lambda value: abs(value)),
        breach_duration_minutes=float(len(action_hits)),
        alert_duration_minutes=float(len(alert_hits)),
        critical_duration_minutes=float(len(critical_hits)),
        severity=severity,
        outcome=outcome,
        confidence=confidence,
        confidence_explanation=confidence_explanation,
        limit_summary={
            "validated_range": limits.validated_range.model_dump() if limits.validated_range else None,
            "alert_limit": limits.alert_limit.model_dump() if limits.alert_limit else None,
            "action_limit": limits.action_limit.model_dump() if limits.action_limit else None,
            "critical_limit": limits.critical_limit.model_dump() if limits.critical_limit else None,
        },
        first_breach_timestamp=first_breach_timestamp,
        last_breach_timestamp=last_breach_timestamp,
        total_breach_minutes=total_breach_minutes,
        longest_continuous_breach_minutes=longest_continuous_breach_minutes,
        evidence_references=evidence_references,
        confidence_breakdown=confidence_breakdown,
    )


def evaluate_state_of_control(
    observations: list[ParameterObservation],
    parameter_limits: list[ParameterLimits],
    *,
    tenant_id: str,
    site_id: str,
    area_id: str,
    asset_id: str,
    room_id: str | None = None,
    batch_id: str | None = None,
    product_id: str | None = None,
    material_lot_id: str | None = None,
    operation: str | None = None,
    phase: str | None = None,
    scenario_id: str | None = None,
    source_system: str = "demo_source",
    source_protocol: str = "MQTT",
    connector_id: str = "demo-connector",
) -> StateOfControlAssessment:
    if not parameter_limits:
        raise ValueError("parameter_limits must not be empty")

    grouped: dict[str, list[ParameterObservation]] = {limits.parameter: [] for limits in parameter_limits}
    for observation in observations:
        grouped.setdefault(observation.parameter, []).append(observation)

    parameter_assessments: list[ParameterAssessment] = []
    for limits in parameter_limits:
        parameter_observations = grouped.get(limits.parameter, [])
        if not parameter_observations:
            continue
        parameter_assessments.append(_evaluate_parameter(parameter_observations, limits))

    if not parameter_assessments:
        primary_limits = parameter_limits[0]
        return StateOfControlAssessment(
            assessment_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            site_id=site_id,
            area_id=area_id,
            asset_id=asset_id,
            room_id=room_id,
            material_lot_id=material_lot_id,
            operation=operation,
            phase=phase,
            metric=primary_limits.parameter,
            outcome=AssessmentOutcome.IN_CONTROL,
            excursion_duration_minutes=0.0,
            action_limit=_extract_limit_value(primary_limits.action_limit),
            alert_limit=_extract_limit_value(primary_limits.alert_limit),
            critical_limit=_extract_limit_value(primary_limits.critical_limit),
            validated_range=primary_limits.validated_range.model_dump() if primary_limits.validated_range else None,
            peak_value=0.0,
            batch_id=batch_id,
            product_id=product_id,
            severity="info",
            confidence=0.5,
            confidence_explanation="No observations were available for assessment.",
            scenario_id=scenario_id,
            duration_window_minutes=primary_limits.duration_window_minutes,
        )

    highest = max(parameter_assessments, key=lambda assessment: _severity_rank(assessment.severity))
    overall_outcome = highest.outcome
    primary_limits = next(limits for limits in parameter_limits if limits.parameter == highest.parameter)
    all_observations = [observation for group in grouped.values() for observation in group]
    breach_candidates = [
        observation
        for observation in all_observations
        if _outside_band(observation.value, primary_limits.action_limit) and observation.parameter == highest.parameter
    ]
    breach_start = breach_candidates[0].timestamp if breach_candidates else None
    breach_end = breach_candidates[-1].timestamp if breach_candidates else None
    confidence = round(min(assessment.confidence for assessment in parameter_assessments), 2)

    confidence_breakdown = highest.confidence_breakdown.copy()
    confidence_breakdown["context_present"] = bool(batch_id or product_id or site_id)

    return StateOfControlAssessment(
        assessment_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        site_id=site_id,
        area_id=area_id,
        asset_id=asset_id,
        room_id=room_id,
        material_lot_id=material_lot_id,
        operation=operation,
        phase=phase,
        metric=highest.parameter,
        outcome=overall_outcome,
        excursion_duration_minutes=max(assessment.breach_duration_minutes for assessment in parameter_assessments),
        breach_start=breach_start,
        breach_end=breach_end,
        action_limit=_extract_limit_value(primary_limits.action_limit),
        alert_limit=_extract_limit_value(primary_limits.alert_limit),
        critical_limit=_extract_limit_value(primary_limits.critical_limit),
        validated_range=primary_limits.validated_range.model_dump() if primary_limits.validated_range else None,
        peak_value=highest.peak_value,
        batch_id=batch_id,
        product_id=product_id,
        severity=highest.severity,
        confidence=confidence,
        confidence_explanation=highest.confidence_explanation,
        scenario_id=scenario_id,
        duration_window_minutes=primary_limits.duration_window_minutes,
        parameter_assessments=[assessment.model_dump() for assessment in parameter_assessments],
        source_lineage={
            "tenant_id": tenant_id,
            "site_id": site_id,
            "area_id": area_id,
            "room_id": room_id,
            "asset_id": asset_id,
            "batch_id": batch_id,
            "product_id": product_id,
            "material_lot_id": material_lot_id,
            "operation": operation,
            "phase": phase,
            "source_system": source_system,
            "source_protocol": source_protocol,
            "connector_id": connector_id,
            "quality": min((observation.quality for observation in all_observations), default="GOOD"),
            "source_record_reference": f"{asset_id}:{highest.parameter}",
        },
        confidence_breakdown=confidence_breakdown,
    )


# ---------------------------------------------------------------------------
# Backward-compatible Week 5 humidity helpers
# ---------------------------------------------------------------------------

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
    """Evaluate a relative-humidity reading stream against alert/action limits."""
    observations = [
        ParameterObservation(
            parameter="relative_humidity",
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp,
            quality=reading.quality,
            source_system=reading.source_system or "bms_simulation",
        )
        for reading in readings
    ]
    assessment = evaluate_state_of_control(
        observations=observations,
        parameter_limits=[
            ParameterLimits(
                parameter="relative_humidity",
                unit="%RH",
                validated_range=LimitBand(max_value=50.0),
                alert_limit=LimitBand(max_value=alert_limit),
                action_limit=LimitBand(max_value=action_limit),
                critical_limit=LimitBand(max_value=action_limit + 5.0),
                duration_window_minutes=1,
            )
        ],
        tenant_id=tenant_id,
        site_id=site_id,
        area_id=area_id,
        asset_id=asset_id,
        batch_id=batch_id,
        product_id=product_id,
        source_system=readings[0].source_system if readings else "bms_simulation",
        source_protocol="simulated",
        connector_id="local-sitewise",
    )
    if not readings:
        assessment.outcome = AssessmentOutcome.IN_CONTROL
        assessment.excursion_duration_minutes = 0.0
        assessment.peak_value = 0.0
    return assessment


def build_assurance_events_from_assessment(
    assessment: StateOfControlAssessment,
) -> list[AssuranceEvent]:
    """Convert a StateOfControlAssessment into one or more typed AssuranceEvents."""
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
                unit="%RH" if assessment.metric == "relative_humidity" else None,
                batch_id=assessment.batch_id,
                product_id=assessment.product_id,
                room_id=assessment.room_id,
                material_lot_id=assessment.material_lot_id,
                operation=assessment.operation,
                phase=assessment.phase,
                source_protocol=assessment.source_lineage.get("source_protocol"),
                connector_id=assessment.source_lineage.get("connector_id"),
                quality=assessment.source_lineage.get("quality", "GOOD"),
                severity=assessment.severity,
                status="open",
                payload={
                    "excursion_duration_minutes": assessment.excursion_duration_minutes,
                    "breach_start": assessment.breach_start.isoformat() if assessment.breach_start else None,
                    "breach_end": assessment.breach_end.isoformat() if assessment.breach_end else None,
                    "action_limit": assessment.action_limit,
                    "alert_limit": assessment.alert_limit,
                    "critical_limit": assessment.critical_limit,
                    "assessment_id": assessment.assessment_id,
                    "scenario_id": assessment.scenario_id,
                    "parameter_assessments": assessment.parameter_assessments,
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
                unit="%RH" if assessment.metric == "relative_humidity" else None,
                batch_id=assessment.batch_id,
                product_id=assessment.product_id,
                room_id=assessment.room_id,
                material_lot_id=assessment.material_lot_id,
                operation=assessment.operation,
                phase=assessment.phase,
                source_protocol=assessment.source_lineage.get("source_protocol"),
                connector_id=assessment.source_lineage.get("connector_id"),
                quality=assessment.source_lineage.get("quality", "GOOD"),
                severity=assessment.severity,
                status="open",
                payload={"alert_limit": assessment.alert_limit, "assessment_id": assessment.assessment_id},
                trace_id=assessment.assessment_id,
            )
        )

    return events
