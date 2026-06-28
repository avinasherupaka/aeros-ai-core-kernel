"""
Areos Kernel API.

FastAPI application exposing the local sandbox/test-harness endpoints and the
Phase 3–5 AWS-native product scaffolding.

Run:
    uvicorn aeros.kernel.api.main:app --reload
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException

from aeros.kernel.api.demo_data import (
    demo_event_bundles,
    get_demo_event_bundle,
    list_demo_events,
    scenario_library,
    workflow_views,
)
from aeros.kernel.assurance.state_of_control import (
    build_assurance_events_from_assessment,
    run_humidity_state_of_control,
)
from aeros.kernel.config.messages import ASSURANCE_POSITIONING, PROOF_POSITIONING
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier
from aeros.kernel.simulation.humidity_excursion import generate_humidity_excursion
from aeros.kernel.simulation.plant_topology import build_osd_topology
from aeros.kernel.storage.local_sitewise import LocalSiteWiseRegistry, MeasurementReading

app = FastAPI(title="Areos Kernel API", version="0.3.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "aeros-kernel",
        "positioning": ASSURANCE_POSITIONING,
        "runtime_mode": "local sandbox/test harness",
    }


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
        "assurance_events": [event.model_dump(mode="json") for event in assurance_events],
    }


@app.get("/ontology/industry-packs")
def industry_packs() -> dict:
    from aeros.kernel.ontology.industry_packs import list_industry_packs

    return {
        "message": PROOF_POSITIONING,
        "industry_packs": list_industry_packs(),
    }


@app.get("/scenario-library")
def get_scenario_library() -> dict:
    return {"scenarios": scenario_library()}


@app.get("/assurance/demo-events")
def assurance_demo_events() -> dict:
    return {"events": list_demo_events()}


@app.get("/assurance/events/{event_id}/state-of-control")
def assurance_event_state(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    return {"scenario_id": bundle.scenario_id, "assessment": bundle.assessment.model_dump(mode="json")}


@app.get("/assurance/events/{event_id}/impact")
def assurance_event_impact(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    return {"scenario_id": bundle.scenario_id, "impact": bundle.impact.model_dump(mode="json")}


@app.get("/assurance/events/{event_id}/evidence-graph")
def assurance_event_evidence_graph(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    return {"scenario_id": bundle.scenario_id, "graph": bundle.evidence_graph.model_dump(mode="json")}


@app.get("/dossiers/events/{event_id}")
def get_event_dossier(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    return bundle.dossier.sections


@app.post("/dossiers/events/{event_id}/generate")
def generate_event_dossier(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
    )
    demo_event_bundles.cache_clear()
    return dossier.model_dump(mode="json")


@app.get("/workflows/deviation-queue")
def deviation_queue() -> dict:
    views = workflow_views()
    return views["deviation_queue"].model_dump(mode="json")


@app.get("/workflows/engineering-reliability-board")
def engineering_reliability_board() -> dict:
    views = workflow_views()
    return views["engineering_reliability_board"].model_dump(mode="json")


@app.get("/workflows/plant-head-assurance")
def plant_head_assurance() -> dict:
    views = workflow_views()
    return views["plant_head_assurance"].model_dump(mode="json")


@app.get("/workflows/validation-audit-room")
def validation_audit_room() -> dict:
    views = workflow_views()
    return views["validation_audit_room"].model_dump(mode="json")


@app.get("/assurance/events/{event_id}/full-package")
def assurance_event_full_package(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    return {
        "event_id": event_id,
        "scenario_id": bundle.scenario_id,
        "assessment": bundle.assessment.model_dump(mode="json"),
        "impact": bundle.impact.model_dump(mode="json"),
        "reliability_insight": bundle.reliability_insight.model_dump(mode="json"),
        "evidence_graph_summary": {
            "node_count": len(bundle.evidence_graph.nodes),
            "edge_count": len(bundle.evidence_graph.edges),
            "node_types": list({node.node_type.value for node in bundle.evidence_graph.nodes}),
        },
        "dossier": bundle.dossier.model_dump(mode="json"),
    }


@app.post("/dossiers/events/{event_id}/generate-package")
def generate_event_full_package(event_id: str) -> dict:
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
    )
    demo_event_bundles.cache_clear()
    return {"package_completeness_score": dossier.package_completeness_score, "dossier": dossier.model_dump(mode="json")}


@app.get("/dossiers/events/{event_id}/manifest")
def get_event_dossier_manifest(event_id: str) -> dict:
    import json
    from pathlib import Path
    
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    manifest_path = bundle.dossier.manifest_path
    if not manifest_path or not Path(manifest_path).exists():
        return {"message": "Manifest not yet generated. POST to /dossiers/events/{event_id}/generate-package first.", "event_id": event_id}
    return json.loads(Path(manifest_path).read_text())


@app.get("/apqr/{site_id}/demo-section")
def get_apqr_demo_section(site_id: str) -> dict:
    views = workflow_views()
    apqr = views["apqr"]
    return apqr.model_dump(mode="json")


@app.post("/apqr/{site_id}/generate-demo-section")
def generate_apqr_demo_section(site_id: str) -> dict:
    from aeros.kernel.dossiers.apqr import build_apqr_section
    
    bundles = list(demo_event_bundles().values())
    events = [b.event for b in bundles]
    impacts = [b.impact for b in bundles]
    insights = [b.reliability_insight for b in bundles]
    section = build_apqr_section(
        site_id=site_id,
        events=events,
        impacts=impacts,
        reliability_insights=insights,
        period="2026-H1",
    )
    return section.model_dump(mode="json")


@app.get("/workflows/deviation-drafts/{event_id}")
def get_deviation_draft(event_id: str) -> dict:
    from aeros.kernel.workflows.deviation_workbench import create_deviation_draft
    
    try:
        bundle = get_demo_event_bundle(event_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}") from exc
    draft = create_deviation_draft(bundle.event, bundle.impact, bundle.dossier)
    return draft.model_dump(mode="json")
