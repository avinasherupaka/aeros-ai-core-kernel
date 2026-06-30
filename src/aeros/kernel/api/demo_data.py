from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from aeros.kernel.assurance.event_to_impact import ImpactAssessment, evaluate_event_impact
from aeros.kernel.assurance.evidence_graph import EvidenceGraphSnapshot, build_evidence_graph
from aeros.kernel.assurance.reliability_intelligence import MaintenanceRecord, ReliabilityInsight, analyze_recurrence
from aeros.kernel.assurance.state_of_control import (
    build_demo_observations_from_scenario,
    build_state_of_control_rules_from_scenario,
    build_assurance_events_from_assessment,
    evaluate_state_of_control,
)
from aeros.kernel.dossiers.apqr import APQRSection, build_apqr_section
from aeros.kernel.dossiers.gmp_dossier import GMPDossier, build_gmp_dossier
from aeros.kernel.models.canonical import AssuranceEvent, StateOfControlAssessment
from aeros.kernel.models.canonical import EventType
from aeros.kernel.ontology.industry_packs import build_demo_ontology_context, get_scenario_definition, list_industry_packs, load_scenario_library
from aeros.kernel.workflows.deviation_workbench import DeviationWorkbenchView, build_deviation_queue
from aeros.kernel.workflows.engineering_reliability_board import EngineeringReliabilityBoard, build_engineering_reliability_board
from aeros.kernel.workflows.plant_head_assurance import PlantHeadAssuranceView, build_plant_head_assurance_view
from aeros.kernel.workflows.validation_audit_room import ValidationAuditRoomView, build_validation_audit_room


class DemoEventBundle(BaseModel):
    scenario_id: str
    assessment: StateOfControlAssessment
    event: AssuranceEvent
    impact: ImpactAssessment
    reliability_insight: ReliabilityInsight
    evidence_graph: EvidenceGraphSnapshot
    dossier: GMPDossier


def _evidence_root() -> Path:
    return Path(__file__).resolve().parents[4] / "artifacts" / "evidence"


def _make_prior_events(event: AssuranceEvent, count: int) -> list[AssuranceEvent]:
    prior_events = []
    for index in range(count):
        prior_event = event.model_copy(deep=True)
        prior_event.event_id = f"{event.event_id}_prior_{index + 1}"
        prior_event.timestamp = event.timestamp - timedelta(days=index + 3)
        prior_events.append(prior_event)
    return prior_events


def _build_bundle(scenario_id: str) -> DemoEventBundle:
    scenario = get_scenario_definition(scenario_id)
    context = build_demo_ontology_context(scenario_id)
    rules = build_state_of_control_rules_from_scenario(scenario)
    observations = build_demo_observations_from_scenario(
        scenario,
        start_time=datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
    )
    default_context = scenario.default_context
    assessment = evaluate_state_of_control(
        observations=observations,
        parameter_limits=rules,
        tenant_id=context.tenant_id,
        site_id=context.site_id,
        area_id=default_context.get("area_id", "area_01"),
        asset_id=default_context.get("utility_system_id") or default_context.get("equipment_id", "asset_01"),
        room_id=default_context.get("room_id"),
        batch_id=default_context.get("batch_id"),
        product_id=default_context.get("product_id"),
        material_lot_id=default_context.get("material_lot_id"),
        operation=default_context.get("operation"),
        phase=default_context.get("phase"),
        scenario_id=scenario_id,
        source_system=scenario.source_systems[0] if scenario.source_systems else "demo",
        source_protocol=scenario.source_protocols[0] if scenario.source_protocols else "MQTT",
        connector_id=f"{scenario_id}-connector",
    )
    assessment.assessment_id = f"assessment::{scenario_id}"
    events = build_assurance_events_from_assessment(assessment)
    event = events[0]
    event.event_id = f"event::{scenario_id}"
    event.asset_id = default_context.get("equipment_id") or event.asset_id
    event.room_id = default_context.get("room_id")
    event.material_lot_id = default_context.get("material_lot_id")
    event.operation = default_context.get("operation")
    event.phase = default_context.get("phase")
    event.source_protocol = scenario.source_protocols[0] if scenario.source_protocols else "MQTT"
    event.connector_id = f"{scenario_id}-connector"
    event.required_evidence = scenario.evidence_checklist
    event.risk_ids = [risk.lower().replace(" ", "_") for risk in scenario.quality_risks]
    event.timestamp = assessment.assessed_at
    if any(system.lower().startswith("labware") or "lims" in system.lower() for system in scenario.source_systems):
        event.event_type = EventType.LIMS_RESULT_ALERT

    available_evidence = scenario.evidence_checklist[: max(1, len(scenario.evidence_checklist) - 1)]
    impact = evaluate_event_impact(event, context, scenario, available_evidence=available_evidence)

    prior_count = 0
    if "humidity" in scenario_id or "temperature" in scenario_id:
        prior_count = 2
    elif "pressure" in scenario_id:
        prior_count = 1
    prior_events = _make_prior_events(event, prior_count)
    maintenance = [
        MaintenanceRecord(
            work_order_id=f"WO::{scenario_id}",
            asset_id=event.asset_id,
            completed_at=event.timestamp - timedelta(days=5),
            summary="Recent maintenance completed on the affected asset.",
        )
    ]
    reliability = analyze_recurrence(event, prior_events, maintenance_records=maintenance)
    evidence_graph = build_evidence_graph(event, context, impact, reliability_insight=reliability)
    dossier = build_gmp_dossier(
        event=event,
        assessment=assessment,
        impact_assessment=impact,
        evidence_graph=evidence_graph,
        reliability_insight=reliability,
        output_root=_evidence_root(),
    )
    return DemoEventBundle(
        scenario_id=scenario_id,
        assessment=assessment,
        event=event,
        impact=impact,
        reliability_insight=reliability,
        evidence_graph=evidence_graph,
        dossier=dossier,
    )


@lru_cache(maxsize=1)
def demo_event_bundles() -> dict[str, DemoEventBundle]:
    bundles = {}
    for pack in load_scenario_library():
        for scenario in pack.scenarios:
            bundles[f"event::{scenario.scenario_id}"] = _build_bundle(scenario.scenario_id)
    return bundles


def get_demo_event_bundle(event_id: str) -> DemoEventBundle:
    bundles = demo_event_bundles()
    if event_id not in bundles:
        raise KeyError(event_id)
    return bundles[event_id]


def list_demo_events() -> list[dict]:
    return [
        {
            "event_id": bundle.event.event_id,
            "scenario_id": bundle.scenario_id,
            "site_id": bundle.event.site_id,
            "metric": bundle.event.metric,
            "severity": bundle.event.severity,
            "batch_id": bundle.event.batch_id,
        }
        for bundle in demo_event_bundles().values()
    ]


def scenario_library() -> list[dict]:
    scenarios = []
    for pack in load_scenario_library():
        for scenario in pack.scenarios:
            scenarios.append(scenario.model_dump(mode="json"))
    return scenarios


def workflow_views() -> dict[str, object]:
    bundles = list(demo_event_bundles().values())
    events = [bundle.event for bundle in bundles]
    impacts = [bundle.impact for bundle in bundles]
    insights = [bundle.reliability_insight for bundle in bundles]
    dossiers = [bundle.dossier for bundle in bundles]
    return {
        "deviation_queue": build_deviation_queue(events, impacts),
        "engineering_reliability_board": build_engineering_reliability_board(site_id="enterprise_demo", events=events, reliability_insights=insights),
        "plant_head_assurance": build_plant_head_assurance_view(site_id="enterprise_demo", events=events, impacts=impacts, reliability_insights=insights),
        "validation_audit_room": build_validation_audit_room(site_id="enterprise_demo", dossiers=dossiers, impacts=impacts),
        "apqr": build_apqr_section(site_id="enterprise_demo", events=events, impacts=impacts, reliability_insights=insights),
    }
