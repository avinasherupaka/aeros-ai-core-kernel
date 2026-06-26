# Week 04 — AWS IoT SiteWise-like Industrial Data Model

## Learning goal

Understand how AWS IoT SiteWise models industrial assets and their time-series data,
and how the local `LocalSiteWiseRegistry` provides the same capabilities without AWS.

---

## What is AWS IoT SiteWise?

SiteWise is AWS's managed service for ingesting, modelling, and querying industrial
time-series data. It introduces three key concepts:

### AssetModel
A reusable schema for a type of asset. Like a class definition.

```
AssetModel: AHU
  Measurements:
    - relative_humidity (%RH)
    - temperature (°C)
    - differential_pressure (Pa)
  Transforms (computed from latest measurement):
    - humidity_state: if rh > 60 then ACTION elif rh > 55 then ALERT else IN_CONTROL
  Metrics (aggregated over time window):
    - excursion_duration: count(relative_humidity > 60) per window
```

### Asset
An instance of an AssetModel. Like an object instantiated from a class.
```
Asset: AHU-03
  model: AHU
  location: Hyderabad Site / OSD Manufacturing / Compression Room 1
```

### Measurement → Transform → Metric pipeline

```
Raw tag value (OPC UA / BMS)
  → Measurement (stored as time-series)
    → Transform (computed per reading)
      → Metric (aggregated over time window)
```

---

## Local implementation: LocalSiteWiseRegistry

`src/aeros/kernel/storage/local_sitewise.py` implements this pattern:

```python
from aeros.kernel.storage.local_sitewise import (
    AssetModel, Asset, Measurement, Transform, Metric,
    MeasurementReading, LocalSiteWiseRegistry,
    classify_humidity_state, compute_action_excursion_minutes,
)

# Define the AssetModel
ahu_model = AssetModel(
    model_id="ahu_model",
    name="AHU",
    measurements=[Measurement(name="relative_humidity", unit="%RH")],
    transforms=[Transform(name="humidity_state",
                          expression="ACTION if rh > 60 else ALERT if rh > 55 else IN_CONTROL")],
    metrics=[Metric(name="excursion_duration",
                    expression="count(relative_humidity > 60) in minutes")],
)

# Register model and asset
registry = LocalSiteWiseRegistry()
registry.register_model(ahu_model)
registry.register_asset(Asset(asset_id="ahu_03", model_id="ahu_model",
                               tenant_id="acme_pharma", site_id="hyd_site_01",
                               area_id="osd_manufacturing"))

# Ingest readings
for event in scenario["events"]:
    registry.record_measurement(MeasurementReading(
        asset_id="ahu_03",
        measurement_name="relative_humidity",
        value=event["value"],
        unit=event["unit"],
        timestamp=datetime.fromisoformat(event["timestamp"]),
    ))

# Apply transform (SiteWise Computed Property equivalent)
transformed = registry.apply_humidity_transform("ahu_03")
# → [{timestamp, value, state: "ACTION"/"ALERT"/"IN_CONTROL"}, ...]

# Compute metric (SiteWise Aggregated Property equivalent)
duration = registry.compute_excursion_duration("ahu_03")
# → 22.0 (minutes)
```

---

## Humidity state classification

The `classify_humidity_state()` function is the SiteWise Transform equivalent:

```
rh > action_limit (60) → ACTION
rh > alert_limit (55)  → ALERT
else                   → IN_CONTROL
```

**Important boundary condition**: the limits are exclusive (>), not inclusive (≥).
A value exactly at the limit is IN_CONTROL / ALERT respectively.

---

## Why this matters for GxP

SiteWise Transforms and Metrics are used to:
1. Show historical state of control on a timeline chart.
2. Compute excursion durations for deviation reports.
3. Feed the state-of-control engine with pre-classified data.

In the Dendrix demo, the metric output is `22.0 minutes above action limit` — this
is the number that goes into the deviation report.

---

## Run / test

```bash
pytest tests/test_local_sitewise.py -v
```

All 11 tests should pass, including:
- `test_classify_humidity_action` — 63 %RH → ACTION
- `test_compute_excursion_returns_22_for_dendrix_scenario` — 22.0 minutes
- `test_registry_apply_humidity_transform` — 22 ACTION states in 60 readings
- `test_registry_compute_excursion_duration_22_minutes` — registry metric = 22.0

---

## AWS equivalent summary

| Local | AWS |
|---|---|
| `AssetModel` | SiteWise AssetModel |
| `Asset` | SiteWise Asset instance |
| `MeasurementReading` | SiteWise AssetProperty value (time-series) |
| `classify_humidity_state()` | SiteWise Transform (computed property) |
| `compute_action_excursion_minutes()` | SiteWise Metric (aggregated property) |
| `LocalSiteWiseRegistry` | SiteWise Asset Property Values API |
| In-memory `_readings` dict | SiteWise time-series storage (S3-backed) |
