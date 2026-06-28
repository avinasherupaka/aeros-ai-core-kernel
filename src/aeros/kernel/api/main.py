"""
Areos Kernel API.

FastAPI application exposing the local MVP endpoints.

Endpoints:
  GET /health                          — liveness check
  GET /topology                        — OSD plant topology
  GET /scenario/humidity-excursion     — raw humidity excursion scenario
  GET /state-of-control/humidity-excursion — state-of-control assessment

Run:
    uvicorn aeros.kernel.api.main:app --reload
"""

from datetime import datetime, timezone

from fastapi import FastAPI

from aeros.kernel.assurance.state_of_control import (
    build_assurance_events_from_assessment,
    run_humidity_state_of_control,
)
from aeros.kernel.simulation.humidity_excursion import generate_humidity_excursion
from aeros.kernel.simulation.plant_topology import build_osd_topology
from aeros.kernel.storage.local_sitewise import LocalSiteWiseRegistry, MeasurementReading

app = FastAPI(title="Areos Kernel API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "aeros-kernel"}


@app.get("/topology")
def topology() -> dict:
    return build_osd_topology()


@app.get("/scenario/humidity-excursion")
def humidity_excursion() -> dict:
    return generate_humidity_excursion()


@app.get("/state-of-control/humidity-excursion")
def state_of_control_humidity_excursion() -> dict:
    """
    Run the state-of-control engine against the Dendrix humidity excursion scenario.

    Returns a StateOfControlAssessment + derived AssuranceEvents.
    Expected result: BREACH_CONFIRMED with excursion_duration_minutes=22.
    """
    scenario = generate_humidity_excursion()
    topology = scenario["topology"]
    asset_id = topology["utility_asset"]["equipment_id"]

    registry = LocalSiteWiseRegistry()
    for event in scenario["events"]:
        registry.record_measurement(
            MeasurementReading(
                asset_id=asset_id,
                measurement_name="relative_humidity",
                value=event["value"],
                unit=event["unit"],
                timestamp=datetime.fromisoformat(event["timestamp"]),
                quality="GOOD",
                source_system="bms_simulation",
            )
        )

    readings = registry.get_readings(asset_id, "relative_humidity")
    assessment = run_humidity_state_of_control(
        readings=readings,
        tenant_id=topology["tenant_id"],
        site_id=topology["site"]["site_id"],
        area_id=topology["area"]["area_id"],
        asset_id=asset_id,
        alert_limit=scenario["limits"]["alert_limit"],
        action_limit=scenario["limits"]["action_limit"],
        batch_id=topology["batch"]["batch_id"],
        product_id=topology["batch"]["product_id"],
    )
    assurance_events = build_assurance_events_from_assessment(assessment)

    return {
        "assessment": assessment.model_dump(mode="json"),
        "assurance_events": [e.model_dump(mode="json") for e in assurance_events],
    }
