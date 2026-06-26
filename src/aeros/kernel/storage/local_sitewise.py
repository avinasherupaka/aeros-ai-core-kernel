"""
Local SiteWise-like industrial data model.

AWS IoT SiteWise models industrial assets as a hierarchy of:
  AssetModel → Asset → Measurement / Transform / Metric

This module is the local MVP equivalent:
  - AssetModel: defines what measurements, transforms, and metrics an asset has.
  - Asset:      an instance of an AssetModel anchored to the ISA-95 hierarchy.
  - MeasurementReading: a single timestamped tag value.
  - LocalSiteWiseRegistry: stores readings in memory and evaluates
      transforms and metrics against the ingested data.

AWS equivalent: AWS IoT SiteWise asset models, asset property values API,
  computed properties (transforms/metrics via expression engine).

Key operations for the humidity scenario:
  - classify_humidity_state(rh) → IN_CONTROL / ALERT / ACTION
  - compute_action_excursion_minutes(readings) → float (e.g. 22.0)

Run tests:
    pytest tests/test_local_sitewise.py
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Measurement(BaseModel):
    name: str
    unit: str
    description: str = ""


class Transform(BaseModel):
    """Human-readable expression documenting the transform logic.
    Actual evaluation is done via Python methods on LocalSiteWiseRegistry."""
    name: str
    expression: str
    description: str = ""


class Metric(BaseModel):
    """Human-readable expression documenting the metric aggregation logic."""
    name: str
    expression: str
    description: str = ""


class AssetModel(BaseModel):
    model_id: str
    name: str
    measurements: list[Measurement] = []
    transforms: list[Transform] = []
    metrics: list[Metric] = []


class Asset(BaseModel):
    asset_id: str
    model_id: str
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str = ""
    description: str = ""


class MeasurementReading(BaseModel):
    asset_id: str
    measurement_name: str
    value: float
    unit: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality: str = "GOOD"
    source_system: str = ""


# ---------------------------------------------------------------------------
# Humidity state classification (SiteWise Transform equivalent)
# ---------------------------------------------------------------------------

class HumidityState:
    IN_CONTROL = "IN_CONTROL"
    ALERT = "ALERT"
    ACTION = "ACTION"


def classify_humidity_state(rh: float, alert_limit: float = 55.0, action_limit: float = 60.0) -> str:
    """
    SiteWise Transform equivalent:
        if rh > action_limit → ACTION
        elif rh > alert_limit → ALERT
        else → IN_CONTROL
    """
    if rh > action_limit:
        return HumidityState.ACTION
    elif rh > alert_limit:
        return HumidityState.ALERT
    return HumidityState.IN_CONTROL


# ---------------------------------------------------------------------------
# Excursion duration metric (SiteWise Metric equivalent)
# ---------------------------------------------------------------------------

def compute_action_excursion_minutes(
    readings: list[MeasurementReading],
    action_limit: float = 60.0,
) -> float:
    """
    SiteWise Metric equivalent:
        Count readings above action_limit (each reading represents 1 minute in the demo).
    Returns the number of minutes in ACTION state.
    """
    return float(sum(1 for r in readings if r.value > action_limit))


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class LocalSiteWiseRegistry:
    """In-memory store of asset models, assets, and measurement readings."""

    def __init__(self) -> None:
        self.asset_models: dict[str, AssetModel] = {}
        self.assets: dict[str, Asset] = {}
        self._readings: dict[str, list[MeasurementReading]] = defaultdict(list)

    # --- Registration -------------------------------------------------------

    def register_model(self, model: AssetModel) -> None:
        self.asset_models[model.model_id] = model

    def register_asset(self, asset: Asset) -> None:
        self.assets[asset.asset_id] = asset

    # --- Ingestion ----------------------------------------------------------

    def record_measurement(self, reading: MeasurementReading) -> None:
        """Store a single measurement reading."""
        key = f"{reading.asset_id}:{reading.measurement_name}"
        self._readings[key].append(reading)

    def record_measurements(self, readings: list[MeasurementReading]) -> None:
        """Store a batch of readings."""
        for r in readings:
            self.record_measurement(r)

    # --- Query --------------------------------------------------------------

    def get_readings(self, asset_id: str, measurement_name: str) -> list[MeasurementReading]:
        """Return all stored readings for a given asset and measurement."""
        key = f"{asset_id}:{measurement_name}"
        return list(self._readings[key])

    # --- Transforms (SiteWise Computed Properties) --------------------------

    def apply_humidity_transform(
        self,
        asset_id: str,
        alert_limit: float = 55.0,
        action_limit: float = 60.0,
    ) -> list[dict]:
        """
        Apply the humidity-state transform to all stored RH readings.
        Returns a list of {timestamp, value, state} dicts.
        """
        readings = self.get_readings(asset_id, "relative_humidity")
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": r.value,
                "state": classify_humidity_state(r.value, alert_limit, action_limit),
            }
            for r in readings
        ]

    # --- Metrics (SiteWise Aggregated Properties) ---------------------------

    def compute_excursion_duration(
        self,
        asset_id: str,
        measurement_name: str = "relative_humidity",
        action_limit: float = 60.0,
    ) -> float:
        """
        Compute the action-excursion duration in minutes.
        Returns 22.0 for the Dendrix demo scenario.
        """
        readings = self.get_readings(asset_id, measurement_name)
        return compute_action_excursion_minutes(readings, action_limit)
