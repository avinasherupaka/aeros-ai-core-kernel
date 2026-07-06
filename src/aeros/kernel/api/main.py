"""
Areos Kernel API.

FastAPI application exposing the local sandbox/test-harness endpoints and the
Phase 3–5 AWS-native product scaffolding.

Run:
    uvicorn aeros.kernel.api.main:app --reload
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
from aeros.kernel.control_plane import (
    ControlPlaneAssistantQuery,
    build_control_plane_assistant_answer,
    build_control_plane_snapshot,
    render_control_plane_html,
)
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier
from aeros.kernel.simulation.humidity_excursion import generate_humidity_excursion
from aeros.kernel.simulation.plant_topology import build_osd_topology
from aeros.kernel.storage.local_sitewise import LocalSiteWiseRegistry, MeasurementReading

app = FastAPI(title="Areos Kernel API", version="0.3.0")
_cors_origins = os.getenv(
    "AREOS_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in _cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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


@app.get("/control-plane", response_class=HTMLResponse)
def control_plane_ui() -> str:
    return render_control_plane_html()


@app.get("/control-plane/api/overview")
def control_plane_overview() -> dict:
    return build_control_plane_snapshot()


@app.get("/control-plane/api/topology")
def control_plane_topology() -> dict:
    return build_control_plane_snapshot()["topology"]


@app.get("/control-plane/api/readiness")
def control_plane_readiness() -> dict:
    return build_control_plane_snapshot()["readiness"]


@app.get("/control-plane/api/data-flows")
def control_plane_data_flows() -> dict:
    return build_control_plane_snapshot()["data_flows"]


@app.get("/control-plane/api/personas/{persona}")
def control_plane_persona(persona: str) -> dict:
    personas = build_control_plane_snapshot()["personas"]
    if persona not in personas:
        raise HTTPException(status_code=404, detail=f"Unknown persona: {persona}")
    return personas[persona]


@app.post("/control-plane/api/assistant/query")
def control_plane_assistant_query(body: ControlPlaneAssistantQuery) -> dict:
    return build_control_plane_assistant_answer(body)

# ---- New mission-critical endpoints (Phase 8 re-architecture) ----

from aeros.kernel.algorithms.fingerprints import EventFingerprintInput, compute_event_fingerprint
from aeros.kernel.algorithms.idempotency import DynamoDBIdempotencyRegistry, IdempotencyRegistry
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
from aeros.kernel.bedrock.runtime_client import BedrockRuntimeClient
from aeros.kernel.bedrock.runtime_contracts import BedrockRuntimeMode, BedrockResponseEnvelope, BedrockGroundingPolicy
from aeros.kernel.data_backbone.bronze_writer import LocalBronzeWriter, S3BronzeWriter

_idempotency_table_name = os.getenv("AREOS_IDEMPOTENCY_DDB_TABLE", "").strip()
_bronze_bucket = os.getenv("AREOS_BRONZE_BUCKET", "").strip()
_local_bronze_root = os.getenv(
    "AREOS_LOCAL_BRONZE_ROOT",
    str(Path(__file__).resolve().parents[4] / "artifacts" / "lakehouse"),
)
if _idempotency_table_name:
    _event_api_registry = DynamoDBIdempotencyRegistry(
        table_name=_idempotency_table_name,
        region_name=os.getenv("AWS_REGION", "ap-south-1"),
        endpoint_url=os.getenv("AREOS_DYNAMODB_ENDPOINT_URL"),
    )
else:
    _event_api_registry = IdempotencyRegistry()
_event_api_connector = EventApiConnector(
    tenant_id='demo_tenant',
    site_id='demo_site',
    idempotency_registry=_event_api_registry,
    bronze_writer=(
        S3BronzeWriter(bucket_name=_bronze_bucket, region_name=os.getenv("AWS_REGION", "ap-south-1"))
        if _bronze_bucket
        else LocalBronzeWriter(_local_bronze_root)
    ),
)
_bedrock_client = BedrockRuntimeClient(
    model_id=os.getenv("AREOS_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
    guardrail_id=os.getenv("AREOS_BEDROCK_GUARDRAIL_ID", ""),
    guardrail_version=os.getenv("AREOS_BEDROCK_GUARDRAIL_VERSION", ""),
)


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
    try:
        mode = BedrockRuntimeMode(body.mode)
    except ValueError:
        mode = BedrockRuntimeMode.NARRATIVE_RENDERING
    original_guardrail_result = check_guardrails(body.rendered_text)
    envelope = _bedrock_client.render(
        deterministic_answer_id=body.answer_id,
        prompt=body.rendered_text,
        mode=mode,
    )
    return {
        'response_id': envelope.response_id,
        'mode': envelope.mode.value,
        'deterministic_answer_id': envelope.deterministic_answer_id,
        'rendered_text': envelope.rendered_text,
        'disclaimer': envelope.disclaimer,
        'human_approval_required': envelope.human_approval_required,
        'guardrail_passed': original_guardrail_result.passed,
        'guardrail_violations': [
            {'rule': v.rule, 'matched_phrase': v.matched_phrase}
            for v in original_guardrail_result.violations
        ],
    }


# ---- Enterprise Control Plane v2 Routes ----
from aeros.kernel.control_plane.models import (
    AssistantResponse,
    ConnectorStatusCard,
    DataFlowEdge,
    DossierReadinessCard,
    EnterpriseReadinessRollup,
    ManufacturingSiteTopology,
    PersonaWorkflowCard,
    ReadinessScore,
    SiteHealthCard,
    SiteReadinessRollup,
    TopologyNode,
    validate_no_infra_leak,
)


_CP_PERSONA_ALIASES = {
    "system_admin": "system_admin",
    "qa": "qa",
    "plant_ops": "plant_ops",
    "engineering": "engineering",
    "leadership": "leadership",
    "ops": "plant_ops",
}


def _cp_slug(value: str) -> str:
    return value.lower().replace(" ", "-").replace("/", "-").replace("->", "-").replace("_", "-")


def _cp_status(value: str | None) -> str:
    normalized = (value or "unknown").lower()
    if normalized in {"green", "healthy", "ok", "success", "connected", "up"}:
        return "green"
    if normalized in {"yellow", "warning", "degraded", "stale", "at_risk"}:
        return "yellow"
    if normalized in {"red", "failed", "error", "down", "critical", "unhealthy"}:
        return "red"
    return "unknown"


def _cp_aggregate(statuses: list[str], default: str = "unknown") -> str:
    normalized = [_cp_status(status) for status in statuses if status]
    if not normalized:
        return default
    if "red" in normalized:
        return "red"
    if "yellow" in normalized:
        return "yellow"
    if "green" in normalized:
        return "green"
    return default


def _cp_assert_safe(payload: dict) -> dict:
    violations = validate_no_infra_leak(payload)
    if violations:
        raise HTTPException(
            status_code=500,
            detail={"message": "Infrastructure masking validation failed.", "violations": violations},
        )
    return payload


def _cp_snapshot() -> dict:
    return build_control_plane_snapshot()


def _cp_connector_cards() -> list[ConnectorStatusCard]:
    manifests = {item["connector_id"]: item for item in connector_registry.list_connectors()}
    cards: list[ConnectorStatusCard] = []
    for health in connector_registry.health():
        manifest = manifests.get(health["connector_id"], {})
        status = _cp_status(health.get("status"))
        system_type = str(manifest.get("connector_type", "system")).upper()
        recommended_action = None if status == "green" else "Review source-system connectivity and connector retry posture."
        cards.append(
            ConnectorStatusCard(
                connector_label=str(manifest.get("source_system", system_type)),
                system_type=system_type,
                status=status,
                last_ingestion_label="Recently synchronized",
                latency_ms=None,
                latency_status=status if status in {"red", "yellow"} else "green",
                polling_interval_s=None,
                records_last_hour=None,
                sla_breach=status == "red",
                degradation_reason=None if status == "green" else str(health.get("details", {}).get("reason", "Connector requires attention.")),
                recommended_action=recommended_action,
                _connector_id=health["connector_id"],
            )
        )
    return cards


def _cp_site_health_cards(snapshot: dict) -> list[SiteHealthCard]:
    readiness = snapshot.get("readiness", {})
    stages = readiness.get("stages", [])
    connector_status = _cp_aggregate([card.status for card in _cp_connector_cards()], default="unknown")
    evidence_status = _cp_aggregate([
        stage.get("status")
        for stage in stages
        if stage.get("stage_label") == "Dossier readiness"
    ], default="unknown")
    audit_status = evidence_status
    data_freshness = _cp_aggregate([flow.get("status") for flow in snapshot.get("data_flows", {}).get("connections", [])], default="unknown")
    cards: list[SiteHealthCard] = []
    for index, site in enumerate(snapshot.get("topology", {}).get("sites", []), start=1):
        assets = [asset for area in site.get("areas", []) for asset in area.get("assets", [])]
        site_id = next((asset.get("site_id") for asset in assets if asset.get("site_id")), f"site_{index:02d}")
        critical_events = sum(
            1
            for asset in assets
            for event in asset.get("latest_events", [])
            if str(event.get("severity", "")).lower() in {"critical", "high"}
        )
        open_events = sum(len(asset.get("latest_events", [])) for asset in assets)
        cards.append(
            SiteHealthCard(
                site_id=site_id,
                site_label=site.get("site_label", f"Manufacturing Site {index}"),
                archetype=site.get("site_archetype", "General Manufacturing"),
                overall_status=_cp_status(site.get("status")),
                equipment_health=_cp_aggregate([asset.get("status") for asset in assets], default=_cp_status(site.get("status"))),
                connector_health=connector_status,
                data_freshness=data_freshness,
                evidence_completeness=evidence_status,
                audit_readiness=audit_status,
                open_events=open_events,
                critical_events=critical_events,
                business_summary=f"{open_events} tracked event(s) across {len(assets)} asset(s) for {site.get('site_label', 'the site')}.",
                recommended_action=None if _cp_status(site.get("status")) == "green" else "Prioritize the highest-risk asset and close supporting evidence gaps.",
                last_updated=datetime.now(timezone.utc),
            )
        )
    return cards


def _cp_site_rollups(snapshot: dict) -> list[SiteReadinessRollup]:
    cards = _cp_site_health_cards(snapshot)
    return [
        SiteReadinessRollup(
            site_label=card.site_label,
            archetype=card.archetype,
            overall_status=card.overall_status,
            dimensions=[
                ReadinessScore(
                    dimension="Equipment Health",
                    status=card.equipment_health,
                    score_pct=100 if card.equipment_health == "green" else 70 if card.equipment_health == "yellow" else 40,
                    reason_codes=[f"open_events:{card.open_events}", f"critical_events:{card.critical_events}"],
                    recommended_actions=["Stabilize the most degraded equipment cluster first."],
                ),
                ReadinessScore(
                    dimension="Connector Health",
                    status=card.connector_health,
                    score_pct=100 if card.connector_health == "green" else 75 if card.connector_health == "yellow" else 45,
                    reason_codes=[f"connector_status:{card.connector_health}"],
                    recommended_actions=["Review upstream source-system health and connector coverage."],
                ),
                ReadinessScore(
                    dimension="Audit Readiness",
                    status=card.audit_readiness,
                    score_pct=100 if card.audit_readiness == "green" else 70 if card.audit_readiness == "yellow" else 40,
                    reason_codes=[f"evidence_status:{card.evidence_completeness}"],
                    recommended_actions=["Resolve missing evidence before QA disposition."],
                ),
            ],
            plant_risk_summary=card.business_summary,
            qa_release_posture="ready" if card.overall_status == "green" else "review_required",
            audit_readiness_posture="audit_ready" if card.audit_readiness == "green" else "remediation_open",
            open_capas=card.critical_events,
            overdue_reviews=max(card.open_events - card.critical_events, 0),
            last_updated=card.last_updated,
        )
        for card in cards
    ]


def _cp_site_topologies(snapshot: dict) -> list[ManufacturingSiteTopology]:
    topologies: list[ManufacturingSiteTopology] = []
    edge_templates = snapshot.get("data_flows", {}).get("connections", [])
    for site in snapshot.get("topology", {}).get("sites", []):
        site_label = site.get("site_label", "Manufacturing Site")
        site_node_id = _cp_slug(site_label)
        nodes = [
            TopologyNode(
                node_id=site_node_id,
                node_label=site_label,
                node_type="site",
                status=_cp_status(site.get("status")),
                metadata={"archetype": site.get("site_archetype", "General Manufacturing")},
            )
        ]
        for area in site.get("areas", []):
            area_label = area.get("area_label", "Area")
            area_node_id = f"{site_node_id}-{_cp_slug(area_label)}"
            nodes.append(
                TopologyNode(
                    node_id=area_node_id,
                    node_label=area_label,
                    node_type="area",
                    status=_cp_status(area.get("status")),
                    parent_id=site_node_id,
                    metadata={},
                )
            )
            for asset in area.get("assets", []):
                asset_label = asset.get("asset_label", "Asset")
                nodes.append(
                    TopologyNode(
                        node_id=f"{area_node_id}-{_cp_slug(asset_label)}",
                        node_label=asset_label,
                        node_type="asset",
                        status=_cp_status(asset.get("status")),
                        parent_id=area_node_id,
                        metadata={"domain_path": asset.get("domain_path", "")},
                    )
                )
        edges = [
            DataFlowEdge(
                source_label=flow.get("source", "Source"),
                target_label=flow.get("target", "Target"),
                flow_type="workflow" if "QA" in str(flow.get("target")) or "Assistant" in str(flow.get("target")) else "telemetry",
                status=_cp_status(flow.get("status")),
                latency_label=f"{flow['latency_ms']} ms" if flow.get("latency_ms") is not None else None,
                data_rate_label=(f"{flow['records_out']} msgs/run" if flow.get("records_out") is not None else None),
                last_data_label="Current validation snapshot",
                degradation_reason=flow.get("reason"),
            )
            for flow in edge_templates
        ]
        automation_labels = [
            "PLC",
            "BMS",
            "Historian",
            "MES",
            "LIMS",
            "QMS",
            "ERP",
            "CMMS",
            "IoT",
            "SiteWise",
            "Evidence",
            "Workflow",
            "UI",
            "MCP",
        ]
        automation_pyramid = [
            TopologyNode(
                node_id=f"{site_node_id}-automation-{idx}",
                node_label=label,
                node_type="system",
                status="green",
                parent_id=site_node_id,
                metadata={"tier": str(idx + 1)},
            )
            for idx, label in enumerate(automation_labels)
        ]
        topologies.append(
            ManufacturingSiteTopology(
                site_label=site_label,
                archetype=site.get("site_archetype", "General Manufacturing"),
                nodes=nodes,
                edges=edges,
                automation_pyramid=automation_pyramid,
                last_updated=datetime.now(timezone.utc),
            )
        )
    return topologies


def _cp_persona_card(snapshot: dict, persona: str) -> PersonaWorkflowCard:
    persona_key = _CP_PERSONA_ALIASES.get(persona, persona)
    if persona_key not in {"system_admin", "qa", "plant_ops", "engineering", "leadership"}:
        raise HTTPException(status_code=404, detail=f"Unknown persona: {persona}")
    backing_key = persona_key if persona_key in snapshot.get("personas", {}) else ("system_admin" if persona_key == "engineering" else "plant_ops")
    persona_snapshot = snapshot.get("personas", {}).get(backing_key, {})
    status = _cp_status(snapshot.get("readiness", {}).get("overall_status"))
    return PersonaWorkflowCard(
        persona=persona_key,
        persona_label=persona_snapshot.get("label", persona_key.replace("_", " ").title()),
        primary_objective=persona_snapshot.get("objective", "Coordinate readiness and response actions."),
        kpis=[
            {
                "label": str(item.get("name", "KPI")),
                "value": str(item.get("value", "n/a")),
                "status": _cp_status(item.get("status", status)),
                "trend": "stable",
            }
            for item in persona_snapshot.get("kpis", [])
        ],
        alerts=[
            {
                "severity": status,
                "summary": str(highlight),
                "owner": "Control Plane",
                "due": "Review now",
            }
            for highlight in persona_snapshot.get("highlights", [])[:5]
        ],
        recommended_actions=[
            {
                "action": str(action),
                "priority": "high" if index == 0 else "medium",
                "rationale": f"{persona_snapshot.get('label', 'Persona')} guidance from the latest control-plane snapshot.",
            }
            for index, action in enumerate(persona_snapshot.get("recommended_actions", [])[:5])
        ],
        workflow_state={
            "snapshot_source": "build_control_plane_snapshot",
            "overall_status": status,
            "persona_key": persona_key,
        },
    )


def _cp_dossier_card(batch_id: str) -> DossierReadinessCard:
    site_cards = {card.site_id: card.site_label for card in _cp_site_health_cards(_cp_snapshot())}
    for bundle in demo_event_bundles().values():
        if bundle.event.batch_id == batch_id:
            completeness_pct = int(round(getattr(bundle.dossier, "package_completeness_score", 0.0) * 100))
            missing_evidence = list(getattr(bundle.impact, "missing_evidence", []))
            status = "green" if completeness_pct >= 90 and not missing_evidence else "yellow" if completeness_pct >= 70 else "red"
            return DossierReadinessCard(
                batch_id=bundle.event.batch_id,
                batch_label=f"Batch {bundle.event.batch_id}",
                product_label=bundle.event.product_id or "Unspecified Product",
                site_label=site_cards.get(bundle.event.site_id, bundle.event.site_id.replace("_", " ").title()),
                dossier_status=status,
                completeness_pct=completeness_pct,
                missing_evidence=missing_evidence,
                open_capas=len(missing_evidence),
                qa_review_status="pending_human_review" if missing_evidence else "ready_for_qa",
                human_approval_required=True,
                release_recommendation=(
                    f"Hold — {len(missing_evidence)} open evidence item(s) require QA review."
                    if missing_evidence
                    else "Proceed to QA review with human approval."
                ),
                evidence_citations=[bundle.event.event_id, bundle.scenario_id],
            )
    return DossierReadinessCard(
        batch_id=batch_id,
        batch_label=f"Batch {batch_id}",
        product_label="Unspecified Product",
        site_label="Manufacturing Site",
        dossier_status="unknown",
        completeness_pct=0,
        missing_evidence=["No batch-specific dossier evidence has been mapped yet."],
        open_capas=0,
        qa_review_status="not_started",
        human_approval_required=True,
        release_recommendation="Hold — dossier evidence mapping is not yet complete.",
        evidence_citations=["placeholder:dossier-readiness"],
    )


@app.get("/cp/sites")
def cp_list_sites() -> dict:
    """List all manufacturing sites with domain-safe health cards."""
    cards = _cp_site_health_cards(_cp_snapshot())
    return _cp_assert_safe({"sites": [card.model_dump(mode="json") for card in cards]})


@app.get("/cp/sites/{site_id}/health")
def cp_site_health(site_id: str) -> dict:
    """Get domain-safe health card for a specific site."""
    cards = _cp_site_health_cards(_cp_snapshot())
    match = next(
        (
            card
            for card in cards
            if site_id in {card.site_id, _cp_slug(card.site_id), _cp_slug(card.site_label)}
        ),
        None,
    )
    if match is None:
        raise HTTPException(status_code=404, detail=f"Unknown site_id: {site_id}")
    return _cp_assert_safe({"site": match.model_dump(mode="json")})


@app.get("/cp/topology")
def cp_topology() -> dict:
    """Get manufacturing site topology with domain labels. No raw AWS IDs."""
    topologies = _cp_site_topologies(_cp_snapshot())
    return _cp_assert_safe({"topology": [topology.model_dump(mode="json") for topology in topologies]})


@app.get("/cp/connectors")
def cp_connectors() -> dict:
    """List connector status using domain labels only."""
    cards = _cp_connector_cards()
    return _cp_assert_safe({"connectors": [card.model_dump(mode="json") for card in cards]})


@app.get("/cp/readiness")
def cp_readiness() -> dict:
    """Get enterprise readiness rollup with hierarchical scores."""
    rollups = _cp_site_rollups(_cp_snapshot())
    readiness = EnterpriseReadinessRollup(
        overall_status=_cp_aggregate([rollup.overall_status for rollup in rollups]),
        total_sites=len(rollups),
        red_sites=sum(1 for rollup in rollups if rollup.overall_status == "red"),
        yellow_sites=sum(1 for rollup in rollups if rollup.overall_status == "yellow"),
        green_sites=sum(1 for rollup in rollups if rollup.overall_status == "green"),
        sites=rollups,
        enterprise_summary="Enterprise readiness is derived from normalized site health, connector stability, and evidence closure posture.",
        top_risks=[
            rollup.plant_risk_summary
            for rollup in rollups
            if rollup.overall_status in {"red", "yellow"}
        ][:5],
        last_updated=datetime.now(timezone.utc),
    )
    return _cp_assert_safe({"enterprise_readiness": readiness.model_dump(mode="json")})


@app.get("/cp/personas/{persona}/workflow")
def cp_persona_workflow(persona: str) -> dict:
    """Get persona-specific workflow view."""
    card = _cp_persona_card(_cp_snapshot(), persona)
    return _cp_assert_safe({"workflow": card.model_dump(mode="json")})


@app.post("/cp/assistant/query")
def cp_assistant_query(body: ControlPlaneAssistantQuery) -> dict:
    """Query the MCP assistant. Returns domain-safe markdown, never raw JSON."""
    answer = build_control_plane_assistant_answer(body)
    response = AssistantResponse(
        question=body.question,
        persona=body.persona,
        summary=answer.get("summary", "Assistant response generated."),
        response_markdown=answer.get("response_markdown", ""),
        response_format=answer.get("response_format", "markdown"),
        deterministic_facts=[str(item) for item in answer.get("grounding_sources", [])],
        inferred_explanations=[answer.get("summary", "")],
        recommended_actions=[
            line.removeprefix("1. ")
            for line in str(answer.get("response_markdown", "")).splitlines()
            if line.startswith(("1. ", "2. ", "3. "))
        ],
        human_approval_required=bool(answer.get("human_approval_required", False)),
        gxp_decision_deferred=True,
        evidence_citations=[str(item) for item in answer.get("grounding_sources", [])],
    )
    payload = response.model_dump(mode="json")
    violations = validate_no_infra_leak(payload)
    if violations:
        fallback = AssistantResponse(
            question=body.question,
            persona=body.persona,
            summary="A safe response was generated after infrastructure identifiers were redacted.",
            response_markdown="The assistant generated internal-only references. A sanitized control-plane summary has been returned instead.",
            response_format="guided_remediation",
            deterministic_facts=["Infrastructure identifiers were detected and withheld from the UI response."],
            recommended_actions=["Retry the query after narrowing scope to site, batch, or persona context."],
            human_approval_required=True,
            gxp_decision_deferred=True,
            evidence_citations=["sanitization:control-plane-mask"],
            prohibited_content_check_passed=False,
        )
        return fallback.model_dump(mode="json")
    return payload


@app.get("/cp/dossiers/{batch_id}")
def cp_dossier(batch_id: str) -> dict:
    """Get dossier readiness card for a batch."""
    dossier = _cp_dossier_card(batch_id)
    return _cp_assert_safe({"dossier": dossier.model_dump(mode="json")})


@app.get("/cp/capa/queue")
def cp_capa_queue() -> dict:
    """Get CAPA/deviation queue for QA persona."""
    queue = workflow_views().get("deviation_queue").model_dump(mode="json").get("queue", [])
    site_lookup = {card.site_id: card.site_label for card in _cp_site_health_cards(_cp_snapshot())}
    payload = {
        "persona": "qa",
        "queue": [
            {
                "record_id": item.get("event_id", f"capa-{index + 1}"),
                "site_label": site_lookup.get(item.get("site_id", ""), "Manufacturing Site"),
                "summary": item.get("summary", "Deviation/CAPA item awaiting review."),
                "owner": item.get("owner", "QA"),
                "priority": item.get("severity", "medium"),
                "status": item.get("status", "open"),
                "due_label": "Review in current shift",
            }
            for index, item in enumerate(queue)
        ],
    }
    return _cp_assert_safe(payload)


@app.get("/cp/admin/diagnostics")
def cp_admin_diagnostics() -> dict:
    """Admin-only: raw infrastructure diagnostics."""
    snapshot = _cp_snapshot()
    return {
        "mode": "admin_only",
        "control_plane": snapshot.get("control_plane", {}),
        "aws_alignment": snapshot.get("aws_alignment", {}),
        "connector_registry": connector_registry.list_connectors(),
        "connector_health": connector_registry.health(),
    }


# ---- Domain-safe Assurance Event Command Center ----
from aeros.kernel.api.demo_data import demo_event_bundles as _cp_demo_bundles

_CP_SEVERITY_STATUS = {
    "critical": "red",
    "high": "red",
    "major": "yellow",
    "medium": "yellow",
    "low": "green",
    "info": "green",
}

_CP_OUTCOME_STATUS = {
    "BREACH_CONFIRMED": "red",
    "ACTION_REQUIRED": "red",
    "ALERT": "yellow",
    "IN_CONTROL": "green",
}


def _cp_humanize(value: str | None) -> str:
    if not value:
        return "Unspecified"
    return str(value).replace("_", " ").replace("-", " ").replace("::", " ").strip().title()


def _cp_metric_label(metric: str | None) -> str:
    return _cp_humanize(metric)


def _cp_event_summary(bundle) -> dict:
    event = bundle.event
    assessment = bundle.assessment
    outcome = getattr(assessment.outcome, "value", str(assessment.outcome))
    severity = (event.severity or "medium").lower()
    status = _CP_OUTCOME_STATUS.get(outcome, _CP_SEVERITY_STATUS.get(severity, "yellow"))
    return {
        "event_id": event.event_id,
        "title": f"{_cp_metric_label(event.metric)} {_cp_humanize(outcome)}",
        "parameter": _cp_metric_label(event.metric),
        "severity": severity,
        "status": status,
        "outcome": outcome,
        "site_label": _cp_humanize(event.site_id),
        "room_label": _cp_humanize(event.room_id) if event.room_id else None,
        "asset_label": _cp_humanize(event.asset_id),
        "batch_label": event.batch_id if event.batch_id else None,
        "product_label": _cp_humanize(event.product_id) if event.product_id else None,
        "phase_label": _cp_humanize(event.phase) if event.phase else None,
        "duration_minutes": getattr(assessment, "excursion_duration_minutes", None),
        "peak_value": getattr(assessment, "peak_value", None),
        "unit": event.unit,
    }


def _cp_event_series(bundle) -> list[dict]:
    """Build a domain-safe time series for the sparkline from state-of-control observations."""
    series: list[dict] = []
    observations = getattr(bundle.assessment, "observations", None) or []
    for index, obs in enumerate(observations):
        value = getattr(obs, "value", None)
        if value is None and isinstance(obs, dict):
            value = obs.get("value")
        series.append({"t": index, "value": value})
    if not series:
        peak = getattr(bundle.assessment, "peak_value", None)
        if peak is not None:
            base = peak * 0.7
            ramp = [base, base * 1.05, base * 1.15, peak * 0.95, peak, peak * 0.9, base * 1.1, base]
            series = [{"t": i, "value": round(v, 2)} for i, v in enumerate(ramp)]
    return series


def _cp_evidence_graph(bundle) -> dict:
    """Sanitize the evidence graph into domain-safe nodes and edges for the UI."""
    graph = bundle.evidence_graph
    nodes = []
    for node in graph.nodes:
        node_type = getattr(node.node_type, "value", str(node.node_type))
        raw_label = node.label or node.node_id
        # Preserve human-review/approval placeholder labels; humanize infra-like tokens.
        if node_type in {"HumanReview", "Approval"}:
            label = raw_label
        elif node_type in {"Batch"}:
            label = raw_label  # batch IDs are business identifiers
        else:
            label = _cp_humanize(raw_label)
        nodes.append(
            {
                "node_id": node.node_id,
                "node_type": node_type,
                "label": label,
                "attributes": {k: v for k, v in (node.attributes or {}).items() if k not in {"node_type", "label"}},
            }
        )
    edges = [
        {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_type": getattr(edge.edge_type, "value", str(edge.edge_type)),
        }
        for edge in graph.edges
    ]
    return {"nodes": nodes, "edges": edges}


def _cp_required_actions(bundle) -> list[dict]:
    impact = bundle.impact
    missing = list(impact.missing_evidence or [])
    outcome = getattr(bundle.assessment.outcome, "value", str(bundle.assessment.outcome))
    actions = [
        {"label": "State of control assessed", "status": "done"},
        {"label": "Impact evaluated", "status": "done"},
        {
            "label": "Evidence package assembled",
            "status": "done" if not missing else "pending",
        },
    ]
    if missing:
        actions.append({"label": f"Collect {len(missing)} missing evidence item(s)", "status": "pending"})
    if outcome in {"BREACH_CONFIRMED", "ACTION_REQUIRED"}:
        actions.append({"label": "Open CAPA - needs QA assignment", "status": "pending"})
        actions.append({"label": "Batch release BLOCKED pending review", "status": "blocked"})
    return actions


def _cp_command_center(bundle) -> dict:
    event = bundle.event
    impact = bundle.impact
    dossier = bundle.dossier
    summary = _cp_event_summary(bundle)
    completeness = getattr(dossier, "package_completeness_score", None)
    if completeness is not None and completeness <= 1:
        completeness = round(completeness * 100)
    risk_level = "critical" if event.severity in {"critical", "high"} else "medium"
    return {
        "summary": summary,
        "context": {
            "parameter": summary["parameter"],
            "asset_label": summary["asset_label"],
            "room_label": summary["room_label"],
            "batch_label": summary["batch_label"],
            "product_label": summary["product_label"],
            "phase_label": summary["phase_label"],
            "duration_minutes": summary["duration_minutes"],
            "peak_value": summary["peak_value"],
            "unit": summary["unit"],
            "alert_limit": getattr(bundle.assessment, "alert_limit", None),
            "action_limit": getattr(bundle.assessment, "action_limit", None),
        },
        "impact": {
            "risk_level": risk_level,
            "gxp_impact": bool(event.batch_id or event.product_id),
            "capa_required": summary["status"] == "red",
            "confidence_score": impact.confidence_score,
            "confidence_explanation": impact.confidence_explanation,
            "quality_risks": list(impact.likely_quality_risks or []),
        },
        "series": _cp_event_series(bundle),
        "evidence_graph": _cp_evidence_graph(bundle),
        "dossier": {
            "completeness_pct": completeness if completeness is not None else 0,
            "missing_evidence": list(impact.missing_evidence or []),
            "required_evidence": list(impact.required_evidence or []),
        },
        "required_actions": _cp_required_actions(bundle),
    }


@app.get("/cp/events")
def cp_events() -> dict:
    """List domain-safe assurance events for the command center."""
    events = [_cp_event_summary(bundle) for bundle in _cp_demo_bundles().values()]
    events.sort(key=lambda item: {"red": 0, "yellow": 1, "green": 2}.get(item["status"], 3))
    return _cp_assert_safe({"events": events})


@app.get("/cp/events/{event_id}")
def cp_event_detail(event_id: str) -> dict:
    """Full domain-safe command-center payload for one assurance event."""
    bundles = _cp_demo_bundles()
    bundle = bundles.get(event_id)
    if bundle is None:
        match = next((b for b in bundles.values() if _cp_slug(b.event.event_id) == _cp_slug(event_id)), None)
        bundle = match
    if bundle is None:
        raise HTTPException(status_code=404, detail=f"Unknown event_id: {event_id}")
    return _cp_assert_safe({"event": _cp_command_center(bundle)})
