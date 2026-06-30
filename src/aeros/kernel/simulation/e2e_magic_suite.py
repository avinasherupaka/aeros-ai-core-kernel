from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from aeros.kernel.api.main import (
    AgentAskBody,
    ConnectorReplayBody,
    SimulateEventBody,
    ask_agent,
    assurance_event_evidence_graph,
    assurance_event_full_package,
    assurance_event_impact,
    assurance_event_state,
    deviation_queue,
    engineering_reliability_board,
    generate_apqr_demo_section,
    generate_event_dossier,
    generate_event_full_package,
    get_audit_readiness_answer,
    get_connector_health,
    get_connector_registry,
    get_deviation_draft,
    get_enterprise_readiness,
    get_qa_impact_answer,
    plant_head_assurance,
    replay_connector,
    simulate_ingest_event,
    validate_connector,
    validation_audit_room,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")


def run_magic_e2e_suite(output_root: Path | str | None = None, max_replay_records: int = 5) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(output_root or "artifacts/validation/e2e_magic") / stamp
    root.mkdir(parents=True, exist_ok=True)

    connector_ids = (
        "historian-ignition-live",
        "qms-veeva-vault-live",
        "erp-sap-s4-odata-live",
        "cmms-infor-eam-live",
        "lims-labware-live",
    )
    primary_event_id = "event::biotech_bioreactor_ph_excursion"
    secondary_event_id = "event::pharma_osd_humidity_excursion_compression"

    preconditions = {
        "registry": get_connector_registry(),
        "health": get_connector_health(),
        "enterprise_readiness": get_enterprise_readiness(),
    }
    _write_json(root / "01_preconditions" / "preconditions.json", preconditions)

    registered_ids = {item["connector_id"] for item in preconditions["registry"]["connectors"]}
    missing_connectors = [connector_id for connector_id in connector_ids if connector_id not in registered_ids]
    if missing_connectors:
        raise AssertionError(f"Missing expected connectors: {missing_connectors}")

    connector_validation = {}
    connector_replay = {}
    for connector_id in connector_ids:
        connector_validation[connector_id] = validate_connector(connector_id)
        connector_replay[connector_id] = replay_connector(
            connector_id, ConnectorReplayBody(max_records=max_replay_records)
        )

    event_id = f"magic-e2e-{stamp}"
    simulate_request = SimulateEventBody(
        source_system="ignition",
        parameter="bioreactor_temperature",
        value="38.4",
        unit="degC",
        event_id=event_id,
        timestamp="2026-06-01T10:00:00+00:00",
    )
    first_ingestion = simulate_ingest_event(simulate_request)
    second_ingestion = simulate_ingest_event(simulate_request)
    if first_ingestion["is_duplicate"]:
        raise AssertionError("First ingestion should not be duplicate")
    if not second_ingestion["is_duplicate"]:
        raise AssertionError("Second ingestion should be duplicate")

    ingestion = {
        "connector_validation": connector_validation,
        "connector_replay": connector_replay,
        "first_ingestion": first_ingestion,
        "second_ingestion": second_ingestion,
    }
    _write_json(root / "02_ingestion_and_connector_resolution" / "ingestion.json", ingestion)

    assurance = {
        "state": assurance_event_state(primary_event_id),
        "impact": assurance_event_impact(primary_event_id),
        "evidence_graph": assurance_event_evidence_graph(primary_event_id),
        "full_package": assurance_event_full_package(primary_event_id),
        "osd_full_package": assurance_event_full_package(secondary_event_id),
    }
    _write_json(root / "03_assurance_state_and_impact" / "assurance.json", assurance)

    if assurance["state"]["assessment"]["outcome"] not in {"IN_CONTROL", "ALERT", "BREACH_CONFIRMED"}:
        raise AssertionError("Unexpected state-of-control outcome value")

    dossier = {
        "generated": generate_event_dossier(primary_event_id),
        "generated_package": generate_event_full_package(primary_event_id),
        "deviation_draft": get_deviation_draft(primary_event_id),
        "apqr_demo_section": generate_apqr_demo_section("bio_hyd_01"),
    }
    _write_json(root / "04_evidence_graph_and_dossier" / "dossier.json", dossier)

    package_score = dossier["generated_package"]["package_completeness_score"]
    if package_score < 0.7:
        raise AssertionError(f"Package completeness score below threshold: {package_score}")

    generated_manifest = Path(dossier["generated_package"]["dossier"]["manifest_path"])
    if not generated_manifest.exists():
        raise AssertionError(f"Expected dossier manifest to exist: {generated_manifest}")

    workflows_and_answers = {
        "deviation_queue": deviation_queue(),
        "engineering_reliability_board": engineering_reliability_board(),
        "plant_head_assurance": plant_head_assurance(),
        "validation_audit_room": validation_audit_room(),
        "qa_impact_answer": get_qa_impact_answer(primary_event_id),
        "audit_readiness_answer": get_audit_readiness_answer(primary_event_id),
        "qa_agent_response": ask_agent(
            AgentAskBody(
                question="Was BIO-BATCH-204 impacted?",
                persona="qa",
                event_id=primary_event_id,
            )
        ),
    }
    _write_json(root / "05_workflows_answers_and_personas" / "workflows_answers.json", workflows_and_answers)

    summary = {
        "status": "passed",
        "run_root": str(root),
        "events": {
            "primary": primary_event_id,
            "secondary": secondary_event_id,
            "ingestion_replay_event_id": event_id,
        },
        "checks": {
            "first_ingestion_duplicate": first_ingestion["is_duplicate"],
            "second_ingestion_duplicate": second_ingestion["is_duplicate"],
            "state_of_control_outcome": assurance["state"]["assessment"]["outcome"],
            "package_completeness_score": package_score,
            "qa_agent_human_approval_required": workflows_and_answers["qa_agent_response"]["human_approval_required"],
        },
    }
    _write_json(root / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the one-command Areos end-to-end demo and validation suite.")
    parser.add_argument(
        "--output-root",
        default="artifacts/validation/e2e_magic",
        help="Output root where timestamped evidence folders are written.",
    )
    parser.add_argument(
        "--max-replay-records",
        type=int,
        default=5,
        help="Max records to replay per connector during connector replay checks.",
    )
    args = parser.parse_args()
    summary = run_magic_e2e_suite(output_root=args.output_root, max_replay_records=args.max_replay_records)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
