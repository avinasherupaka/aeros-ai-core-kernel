"""
Tests for the state-of-control engine (Week 5).

Validates:
  - BREACH_CONFIRMED outcome for the Dendrix 22-minute scenario.
  - Correct excursion_duration_minutes.
  - Correct source lineage preservation.
  - AssuranceEvent generation from assessment.
  - EventRouter routing to handlers.
  - IN_CONTROL and ALERT outcomes.
  - Empty readings edge case.
"""

from datetime import datetime, timedelta, timezone

import pytest

from aeros.kernel.assurance.state_of_control import (
    build_assurance_events_from_assessment,
    run_humidity_state_of_control,
)
from aeros.kernel.ingestion.event_router import EventRouter, RoutingRule
from aeros.kernel.models.canonical import AssessmentOutcome, EventType
from aeros.kernel.storage.local_sitewise import MeasurementReading


def _make_humidity_readings(profile: list[float]) -> list[MeasurementReading]:
    base = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    return [
        MeasurementReading(
            asset_id="ahu_03",
            measurement_name="relative_humidity",
            value=rh,
            unit="%RH",
            timestamp=base + timedelta(minutes=i),
        )
        for i, rh in enumerate(profile)
    ]


def _dendrix_readings() -> list[MeasurementReading]:
    profile = [49.0] * 20 + [63.0] * 22 + [50.0] * 18
    return _make_humidity_readings(profile)


# ---------------------------------------------------------------------------
# State-of-control outcomes
# ---------------------------------------------------------------------------

def test_breach_confirmed_for_dendrix_scenario():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.outcome == AssessmentOutcome.BREACH_CONFIRMED


def test_excursion_duration_is_22_minutes():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.excursion_duration_minutes == 22.0


def test_peak_value_is_63():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.peak_value == 63.0


def test_source_lineage_preserved():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
        batch_id="BATCH-OSD-2026-001",
        product_id="hygrostatin_10mg_tablet",
    )
    assert assessment.source_lineage["tenant_id"] == "acme_pharma"
    assert assessment.source_lineage["site_id"] == "hyd_site_01"
    assert assessment.source_lineage["asset_id"] == "ahu_03"
    assert assessment.batch_id == "BATCH-OSD-2026-001"
    assert assessment.product_id == "hygrostatin_10mg_tablet"


def test_breach_timestamps_set():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.breach_start is not None
    assert assessment.breach_end is not None
    assert assessment.breach_start < assessment.breach_end


def test_in_control_when_no_breach():
    profile = [49.0] * 30
    readings = _make_humidity_readings(profile)
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.outcome == AssessmentOutcome.IN_CONTROL
    assert assessment.excursion_duration_minutes == 0.0


def test_alert_outcome_when_above_alert_only():
    profile = [57.0] * 10  # above alert (55) but not action (60)
    readings = _make_humidity_readings(profile)
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.outcome == AssessmentOutcome.ALERT
    assert assessment.excursion_duration_minutes == 0.0


def test_empty_readings_returns_in_control():
    assessment = run_humidity_state_of_control(
        readings=[],
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    assert assessment.outcome == AssessmentOutcome.IN_CONTROL
    assert assessment.excursion_duration_minutes == 0.0


# ---------------------------------------------------------------------------
# AssuranceEvent generation
# ---------------------------------------------------------------------------

def test_breach_produces_state_of_control_breach_event():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    events = build_assurance_events_from_assessment(assessment)
    assert len(events) == 1
    assert events[0].event_type == EventType.STATE_OF_CONTROL_BREACH


def test_breach_event_has_correct_tenant_lineage():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
        batch_id="BATCH-OSD-2026-001",
    )
    events = build_assurance_events_from_assessment(assessment)
    event = events[0]
    assert event.tenant_id == "acme_pharma"
    assert event.site_id == "hyd_site_01"
    assert event.batch_id == "BATCH-OSD-2026-001"


def test_in_control_produces_no_events():
    profile = [49.0] * 10
    readings = _make_humidity_readings(profile)
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    events = build_assurance_events_from_assessment(assessment)
    assert len(events) == 0


# ---------------------------------------------------------------------------
# EventRouter
# ---------------------------------------------------------------------------

def test_event_router_routes_to_matching_handler():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    events = build_assurance_events_from_assessment(assessment)

    received = []
    router = EventRouter()
    router.register_rule(RoutingRule(
        rule_id="capture_breach",
        event_type_filter=EventType.STATE_OF_CONTROL_BREACH.value,
        handler=lambda e: received.append(e),
    ))
    router.route_many(events)
    assert len(received) == 1
    assert received[0].event_type == EventType.STATE_OF_CONTROL_BREACH


def test_event_router_wildcard_captures_all():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    events = build_assurance_events_from_assessment(assessment)

    received = []
    router = EventRouter()
    router.register_rule(RoutingRule(rule_id="all", event_type_filter="*", handler=lambda e: received.append(e)))
    router.route_many(events)
    assert len(received) == len(events)


def test_event_router_non_matching_filter_receives_nothing():
    readings = _dendrix_readings()
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
    )
    events = build_assurance_events_from_assessment(assessment)

    received = []
    router = EventRouter()
    router.register_rule(RoutingRule(
        rule_id="only_batch",
        event_type_filter=EventType.BATCH_EVENT.value,
        handler=lambda e: received.append(e),
    ))
    router.route_many(events)
    assert len(received) == 0
