"""
Tests for local SiteWise-like industrial data model (Week 4).

Validates:
  - MeasurementReading storage and retrieval.
  - Humidity state transform (IN_CONTROL / ALERT / ACTION).
  - Action-excursion duration metric (22 minutes for Dendrix scenario).
"""

from datetime import datetime, timedelta, timezone

import pytest

from aeros.kernel.storage.local_sitewise import (
    Asset,
    AssetModel,
    HumidityState,
    LocalSiteWiseRegistry,
    Measurement,
    MeasurementReading,
    Metric,
    Transform,
    classify_humidity_state,
    compute_action_excursion_minutes,
)


# ---------------------------------------------------------------------------
# classify_humidity_state
# ---------------------------------------------------------------------------

def test_classify_humidity_in_control():
    assert classify_humidity_state(49.0) == HumidityState.IN_CONTROL


def test_classify_humidity_alert():
    assert classify_humidity_state(57.0) == HumidityState.ALERT


def test_classify_humidity_action():
    assert classify_humidity_state(63.0) == HumidityState.ACTION


def test_classify_humidity_at_alert_limit_is_in_control():
    # Value must be *above* alert_limit to be ALERT
    assert classify_humidity_state(55.0) == HumidityState.IN_CONTROL


def test_classify_humidity_at_action_limit_is_alert():
    # Value must be *above* action_limit to be ACTION
    assert classify_humidity_state(60.0) == HumidityState.ALERT


# ---------------------------------------------------------------------------
# compute_action_excursion_minutes
# ---------------------------------------------------------------------------

def test_compute_excursion_returns_22_for_dendrix_scenario():
    base = datetime.now(timezone.utc)
    readings = []
    for minute in range(60):
        rh = 63.0 if 20 <= minute < 42 else 49.0
        readings.append(
            MeasurementReading(
                asset_id="ahu_03",
                measurement_name="relative_humidity",
                value=rh,
                unit="%RH",
                timestamp=base + timedelta(minutes=minute),
            )
        )
    assert compute_action_excursion_minutes(readings) == 22.0


def test_compute_excursion_zero_when_no_breach():
    readings = [
        MeasurementReading(asset_id="ahu_03", measurement_name="relative_humidity", value=50.0, unit="%RH")
        for _ in range(10)
    ]
    assert compute_action_excursion_minutes(readings) == 0.0


# ---------------------------------------------------------------------------
# LocalSiteWiseRegistry
# ---------------------------------------------------------------------------

def test_registry_registers_model_and_asset():
    registry = LocalSiteWiseRegistry()
    model = AssetModel(
        model_id="ahu_model",
        name="AHU Model",
        measurements=[Measurement(name="relative_humidity", unit="%RH")],
        transforms=[Transform(name="humidity_state", expression="if rh > 60 then ACTION else IN_CONTROL")],
        metrics=[Metric(name="excursion_duration", expression="count(rh > 60) in minutes")],
    )
    asset = Asset(
        asset_id="ahu_03",
        model_id="ahu_model",
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        room_id="compression_room_1",
    )
    registry.register_model(model)
    registry.register_asset(asset)
    assert "ahu_model" in registry.asset_models
    assert "ahu_03" in registry.assets


def test_registry_record_and_retrieve_readings():
    registry = LocalSiteWiseRegistry()
    reading = MeasurementReading(
        asset_id="ahu_03",
        measurement_name="relative_humidity",
        value=63.0,
        unit="%RH",
    )
    registry.record_measurement(reading)
    readings = registry.get_readings("ahu_03", "relative_humidity")
    assert len(readings) == 1
    assert readings[0].value == 63.0


def test_registry_apply_humidity_transform():
    registry = LocalSiteWiseRegistry()
    base = datetime.now(timezone.utc)
    for minute in range(60):
        rh = 63.0 if 20 <= minute < 42 else 49.0
        registry.record_measurement(
            MeasurementReading(
                asset_id="ahu_03",
                measurement_name="relative_humidity",
                value=rh,
                unit="%RH",
                timestamp=base + timedelta(minutes=minute),
            )
        )
    transformed = registry.apply_humidity_transform("ahu_03")
    assert len(transformed) == 60
    action_states = [t for t in transformed if t["state"] == HumidityState.ACTION]
    assert len(action_states) == 22


def test_registry_compute_excursion_duration_22_minutes():
    registry = LocalSiteWiseRegistry()
    base = datetime.now(timezone.utc)
    for minute in range(60):
        rh = 63.0 if 20 <= minute < 42 else 49.0
        registry.record_measurement(
            MeasurementReading(
                asset_id="ahu_03",
                measurement_name="relative_humidity",
                value=rh,
                unit="%RH",
                timestamp=base + timedelta(minutes=minute),
            )
        )
    duration = registry.compute_excursion_duration("ahu_03")
    assert duration == 22.0
