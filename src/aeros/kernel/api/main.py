"""
Areos Kernel API.

FastAPI application exposing the local sandbox/test-harness endpoints and the
Phase 3–5 AWS-native product scaffolding.

Run:
    uvicorn aeros.kernel.api.main:app --reload
"""

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aeros.kernel.agents import AgentOrchestrator, AgentToolRegistry
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
from aeros.kernel.connectors import ConnectorReplayRequest, default_connector_registry
from aeros.kernel.config.messages import ASSURANCE_POSITIONING, PROOF_POSITIONING
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier
from aeros.kernel.simulation.humidity_excursion import generate_humidity_excursion
from aeros.kernel.simulation.plant_topology import build_osd_topology
from aeros.kernel.storage.local_sitewise import LocalSiteWiseRegistry, MeasurementReading

app = FastAPI(title="Areos Kernel API", version="0.3.0")
connector_registry = default_connector_registry()
agent_tools = AgentToolRegistry()
agent_orchestrator = AgentOrchestrator()


class ConnectorReplayBody(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    max_records: int | None = None
    window_label: str = ""


class AgentAskBody(BaseModel):
    question: str
    persona: str | None = None
    event_id: str | None = None


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


@app.get("/connectors/registry")
def get_connector_registry() -> dict:
    return {"connectors": connector_registry.list_connectors()}


@app.get("/connectors/health")
def get_connector_health() -> dict:
    return {"health": connector_registry.health()}


@app.post("/connectors/{connector_id}/validate")
def validate_connector(connector_id: str) -> dict:
    try:
        return connector_registry.validate(connector_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown connector_id: {connector_id}") from exc


@app.post("/connectors/{connector_id}/replay")
def replay_connector(connector_id: str, body: ConnectorReplayBody) -> dict:
    try:
        return connector_registry.replay(connector_id, ConnectorReplayRequest.model_validate(body.model_dump()))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown connector_id: {connector_id}") from exc


@app.get("/connectors/{connector_id}/validation-pack")
def get_connector_validation_pack(connector_id: str) -> dict:
    try:
        return connector_registry.generate_validation_pack(connector_id, Path(__file__).resolve().parents[4] / "artifacts" / "connectors" / "validation")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown connector_id: {connector_id}") from exc


@app.get("/agents/tools")
def list_agent_tools() -> dict:
    return {"tools": agent_tools.list_tools()}


@app.post("/agents/ask")
def ask_agent(body: AgentAskBody) -> dict:
    return agent_orchestrator.ask(body.question, persona=body.persona, event_id=body.event_id)


@app.get("/enterprise/readiness")
def get_enterprise_readiness() -> dict:
    readiness_path = Path(__file__).resolve().parents[4] / "artifacts" / "release_readiness" / "phase_1_to_7_completeness.json"
    payload = json.loads(readiness_path.read_text()) if readiness_path.exists() else {"phases": [], "status": "pending"}
    return {
        "release_readiness": payload,
        "connector_health": connector_registry.health(),
        "agent_runtime": "local deterministic harness",
    }

# ---- New mission-critical endpoints (Phase 8 re-architecture) ----

from aeros.kernel.algorithms.fingerprints import EventFingerprintInput, compute_event_fingerprint
from aeros.kernel.algorithms.idempotency import IdempotencyRegistry
from aeros.kernel.algorithms.deterministic_answer import (
    AnswerCitation,
    compose_qa_impact_answer,
    compose_audit_readiness_answer,
    compose_engineering_reliability_answer,
)
from aeros.kernel.data_backbone.lakehouse_contracts import ALL_TABLE_CONTRACTS, LakehouseZone
from aeros.kernel.data_backbone.query_contracts import IncidentQuery, execute_stub_query
from aeros.kernel.ingestion.realtime_contracts import IngestionMode, RealtimeSourceType, SourceSystemEvent
from aeros.kernel.ingestion.event_api_connector import EventApiConnector
from aeros.kernel.bedrock.guardrails import check_guardrails
from aeros.kernel.bedrock.runtime_contracts import BedrockRuntimeMode, BedrockResponseEnvelope, BedrockGroundingPolicy

_event_api_connector = EventApiConnector(tenant_id='demo_tenant', site_id='demo_site')
_event_api_registry = IdempotencyRegistry()


def _resolve_demo_bundle(event_id: str):
    candidates = [event_id, f'event::{event_id}']
    for candidate in candidates:
        try:
            return get_demo_event_bundle(candidate)
        except KeyError:
            continue
    bundle_map = demo_event_bundles()
    for key, bundle in bundle_map.items():
        if event_id in {key, bundle.scenario_id, bundle.event.event_id} or event_id in bundle.scenario_id:
            return bundle
    raise HTTPException(status_code=404, detail=f'Unknown event_id: {event_id}')


@app.get('/architecture/data-backbone')
def get_data_backbone_architecture() -> dict:
    """Return data backbone contract summary."""
    from aeros.kernel.algorithms.rule_versioning import DEFAULT_PROCESSING_CONTEXT

    return {
        'target_architecture': 'AWS-native hybrid lakehouse + graph + time-series',
        'zones': [z.value for z in LakehouseZone],
        'table_contracts': [
            {'table_name': t.table_name, 'zone': t.zone.value, 'description': t.description}
            for t in ALL_TABLE_CONTRACTS
        ],
        'backbone_components': {
            'time_series': 'AWS IoT SiteWise',
            'lakehouse': 'S3 + Apache Iceberg + Glue Data Catalog + Lake Formation',
            'graph': 'Amazon Neptune (target); in-memory NetworkX (local sandbox)',
            'workflow_state': 'DynamoDB / Aurora PostgreSQL (target)',
            'semantic_search': 'OpenSearch / Bedrock Knowledge Bases (retrieval only)',
            'rendering': 'Amazon Bedrock (interface layer, not decision engine)',
        },
        'schema_version': DEFAULT_PROCESSING_CONTEXT.schema_version,
    }


@app.get('/architecture/deterministic-algorithms')
def get_deterministic_algorithms() -> dict:
    """Return deterministic algorithm registry summary."""
    from aeros.kernel.algorithms.rule_versioning import DEFAULT_PROCESSING_CONTEXT

    return {
        'kernel_version': DEFAULT_PROCESSING_CONTEXT.kernel_version,
        'schema_version': DEFAULT_PROCESSING_CONTEXT.schema_version,
        'ontology_version': DEFAULT_PROCESSING_CONTEXT.ontology_version,
        'rules': [
            {
                'rule_id': r.rule_id,
                'category': r.rule_category.value,
                'version': r.version,
                'description': r.description,
            }
            for r in DEFAULT_PROCESSING_CONTEXT.rules
        ],
        'determinism_guarantee': (
            'Same input + same rule/schema/code versions → exact same output. '
            'All regulated conclusions are produced by deterministic algorithms, '
            'not by LLM probabilistic inference.'
        ),
    }


class SimulateEventBody(BaseModel):
    source_system: str = 'demo_bms'
    parameter: str = 'temperature'
    value: str = '26.5'
    unit: str = 'degC'
    event_id: str | None = None
    timestamp: str | None = None


@app.post('/ingestion/events/simulate')
def simulate_ingest_event(body: SimulateEventBody) -> dict:
    """Simulate real-time event ingestion (no AWS credentials required)."""
    from datetime import datetime, timezone
    import uuid

    event = SourceSystemEvent(
        event_id=body.event_id or str(uuid.uuid4()),
        source_system=body.source_system,
        source_type=RealtimeSourceType.API_POLLING,
        tenant_id='demo_tenant',
        site_id='demo_site',
        timestamp=body.timestamp or datetime.now(timezone.utc).isoformat(),
        parameter=body.parameter,
        value=body.value,
        unit=body.unit,
    )
    ack = _event_api_connector.ingest_event(event)
    return {
        'fingerprint': ack.fingerprint,
        'is_duplicate': ack.is_duplicate,
        'accepted': ack.accepted,
        'envelope_id': ack.envelope_id,
        'processor_version': ack.processor_version,
        'total_processed': _event_api_connector.processed_count(),
        'total_duplicates': _event_api_connector.duplicate_count(),
    }


@app.post('/answers/qa-impact/{event_id}')
def get_qa_impact_answer(event_id: str) -> dict:
    """Return deterministic QA impact answer for an event."""
    from aeros.kernel.algorithms.rule_versioning import DEFAULT_PROCESSING_CONTEXT
    import uuid

    bundle = _resolve_demo_bundle(event_id)
    impact = bundle.impact
    answer = compose_qa_impact_answer(
        answer_id=str(uuid.uuid4()),
        event_summary=f'{bundle.event.metric} excursion at {bundle.event.asset_id}',
        impacted_batches=[b for b in [bundle.event.batch_id] if b],
        quality_risks=impact.likely_quality_risks[:3],
        evidence_status=(
            impact.evidence_status_list[0].status
            if getattr(impact, 'evidence_status_list', None)
            else 'pending'
        ),
        missing_evidence=impact.missing_evidence if hasattr(impact, 'missing_evidence') else [],
        citations=[
            AnswerCitation(
                source_system='aeros_kernel',
                record_id=bundle.event.event_id,
                record_type='assurance_event',
                timestamp=bundle.event.timestamp.isoformat(),
            )
        ],
        versions={
            'kernel': DEFAULT_PROCESSING_CONTEXT.kernel_version,
            'schema': DEFAULT_PROCESSING_CONTEXT.schema_version,
        },
    )
    return {
        'answer_id': answer.answer_id,
        'answer_type': answer.answer_type.value,
        'answer_text': answer.answer_text,
        'decision_state': answer.decision_state.value,
        'basis_facts': answer.basis_facts,
        'missing_evidence': answer.missing_evidence,
        'human_review_required': answer.human_review_required,
        'generated_from_versions': answer.generated_from_versions,
    }


@app.post('/answers/audit-readiness/{event_id}')
def get_audit_readiness_answer(event_id: str) -> dict:
    """Return deterministic audit readiness answer for an event."""
    from aeros.kernel.algorithms.rule_versioning import DEFAULT_PROCESSING_CONTEXT
    import uuid

    bundle = _resolve_demo_bundle(event_id)
    dossier = bundle.dossier
    answer = compose_audit_readiness_answer(
        answer_id=str(uuid.uuid4()),
        event_id=bundle.event.event_id,
        dossier_completeness_score=(
            dossier.package_completeness_score if hasattr(dossier, 'package_completeness_score') else 0.8
        ),
        missing_evidence=(
            bundle.impact.missing_evidence if hasattr(bundle.impact, 'missing_evidence') else []
        ),
        citations=[
            AnswerCitation(
                source_system='aeros_kernel',
                record_id=bundle.event.event_id,
                record_type='gmp_dossier',
                timestamp=bundle.event.timestamp.isoformat(),
            )
        ],
        versions={
            'kernel': DEFAULT_PROCESSING_CONTEXT.kernel_version,
            'schema': DEFAULT_PROCESSING_CONTEXT.schema_version,
        },
    )
    return {
        'answer_id': answer.answer_id,
        'answer_type': answer.answer_type.value,
        'answer_text': answer.answer_text,
        'decision_state': answer.decision_state.value,
        'missing_evidence': answer.missing_evidence,
        'human_review_required': answer.human_review_required,
    }


class BedrockRenderDraftBody(BaseModel):
    answer_id: str = 'demo_answer_001'
    mode: str = 'narrative_rendering'
    rendered_text: str = 'The humidity excursion event has been assessed. Batch B-2024-001 may have been impacted. Human review required.'


@app.post('/bedrock/render-draft')
def bedrock_render_draft(body: BedrockRenderDraftBody) -> dict:
    """
    Simulate Bedrock rendering a deterministic answer as a narrative.
    Runs guardrail checks on the rendered text.
    No AWS or Bedrock credentials required — local simulation only.
    """
    guardrail_result = check_guardrails(body.rendered_text)
    try:
        mode = BedrockRuntimeMode(body.mode)
    except ValueError:
        mode = BedrockRuntimeMode.NARRATIVE_RENDERING
    envelope = BedrockResponseEnvelope(
        response_id=f'bedrock_render_{body.answer_id}',
        mode=mode,
        deterministic_answer_id=body.answer_id,
        rendered_text=body.rendered_text,
        grounding_policy=BedrockGroundingPolicy(),
        citations=[body.answer_id],
        human_approval_required=True,
    )
    return {
        'response_id': envelope.response_id,
        'mode': envelope.mode.value,
        'deterministic_answer_id': envelope.deterministic_answer_id,
        'rendered_text': envelope.rendered_text,
        'disclaimer': envelope.disclaimer,
        'human_approval_required': envelope.human_approval_required,
        'guardrail_passed': guardrail_result.passed,
        'guardrail_violations': [
            {'rule': v.rule, 'matched_phrase': v.matched_phrase}
            for v in guardrail_result.violations
        ],
    }
