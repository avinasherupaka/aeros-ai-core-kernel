from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from aeros.kernel.api.demo_data import demo_event_bundles, workflow_views

TrafficLight = Literal["green", "yellow", "red"]

SITE_LABELS = {
    "hyd_site_01": "Hyderabad Plant 1",
    "vizag_site_02": "Vizag API Plant 2",
    "blr_bio_01": "Bengaluru Biopharma Campus",
    "bio_hyd_01": "Hyderabad Biopharma Unit",
    "pnq_food_01": "Pune Food Processing Unit",
    "hyd_advanced_01": "Hyderabad Advanced Materials Unit",
}

AREA_LABELS = {
    "osd_manufacturing": "OSD Manufacturing Line",
    "api_reaction": "API Reaction Line",
    "biotech_upstream": "Biopharma Upstream Line",
    "biotech_support": "Biopharma Support Utilities",
    "food_packaging": "Food Packaging Line",
    "advanced_materials": "Advanced Materials Line",
}

ARCHETYPE_BY_SITE = {
    "hyd_site_01": "Chemicals/OSD",
    "vizag_site_02": "Chemicals/API",
    "blr_bio_01": "Biopharma",
    "bio_hyd_01": "Biopharma",
    "pnq_food_01": "Assembly/Food",
    "hyd_advanced_01": "Advanced Materials",
}

ASSET_LABEL_HINTS = {
    "ahu": "AHU",
    "bioreactor": "Bioreactor",
    "cold_room": "Cold Room",
    "reactor": "Reactor",
    "tablet_press": "Tablet Press",
    "wfi_loop": "WFI Loop",
    "packager": "Packager",
    "powder_mixer": "Powder Mixer",
    "dispensing_booth": "Dispensing Booth",
    "solvent_tank": "Solvent Tank",
}


class ControlPlaneAssistantQuery(BaseModel):
    question: str
    persona: str | None = None
    event_id: str | None = None


@dataclass(frozen=True)
class EvidenceRun:
    run_root: Path | None
    summary: dict[str, Any]
    preconditions: dict[str, Any]
    ingestion: dict[str, Any]
    assurance: dict[str, Any]
    dossier: dict[str, Any]
    workflows: dict[str, Any]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _default_e2e_root() -> Path:
    return _repo_root() / "artifacts" / "validation" / "e2e_magic"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _latest_run_root(evidence_root: Path) -> Path | None:
    if not evidence_root.exists():
        return None
    candidates = [path for path in evidence_root.iterdir() if path.is_dir() and (path / "summary.json").exists()]
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def _load_latest_evidence_run(evidence_root: Path | str | None = None) -> EvidenceRun:
    root = _latest_run_root(Path(evidence_root) if evidence_root else _default_e2e_root())
    if root is None:
        return EvidenceRun(None, {}, {}, {}, {}, {}, {})
    return EvidenceRun(
        run_root=root,
        summary=_read_json(root / "summary.json"),
        preconditions=_read_json(root / "01_preconditions" / "preconditions.json"),
        ingestion=_read_json(root / "02_ingestion_and_connector_resolution" / "ingestion.json"),
        assurance=_read_json(root / "03_assurance_state_and_impact" / "assurance.json"),
        dossier=_read_json(root / "04_evidence_graph_and_dossier" / "dossier.json"),
        workflows=_read_json(root / "05_workflows_answers_and_personas" / "workflows_answers.json"),
    )


def _to_title(identifier: str) -> str:
    return identifier.replace("_", " ").replace("-", " ").title()


def _site_label(site_id: str) -> str:
    return SITE_LABELS.get(site_id, _to_title(site_id))


def _area_label(area_id: str) -> str:
    return AREA_LABELS.get(area_id, _to_title(area_id))


def _asset_label(asset_id: str) -> str:
    for hint, label in ASSET_LABEL_HINTS.items():
        if asset_id.startswith(hint):
            suffix = asset_id[len(hint) :].strip("_")
            suffix_label = f" {_to_title(suffix)}" if suffix else ""
            return f"{label}{suffix_label}".strip()
    return _to_title(asset_id)


def _domain_path(site_id: str, area_id: str, asset_id: str) -> str:
    return f"{_site_label(site_id)} -> {_area_label(area_id)} -> {_asset_label(asset_id)}"


def _status_badge(status: str | None) -> TrafficLight:
    normalized = (status or "").lower()
    if normalized in {"critical", "error", "failed", "down", "red"}:
        return "red"
    if normalized in {"degraded", "warning", "high", "medium", "yellow"}:
        return "yellow"
    return "green"


def _aggregate_light(statuses: list[str]) -> TrafficLight:
    if "red" in statuses:
        return "red"
    if "yellow" in statuses:
        return "yellow"
    return "green"


def _severity_light(severity: str, missing_evidence_count: int) -> TrafficLight:
    severity = severity.lower()
    if severity == "critical":
        return "red"
    if severity in {"high", "medium"} or missing_evidence_count > 0:
        return "yellow"
    return "green"


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _duration_ms(start: str | None, end: str | None) -> int | None:
    start_dt = _parse_time(start)
    end_dt = _parse_time(end)
    if not start_dt or not end_dt:
        return None
    return int((end_dt - start_dt).total_seconds() * 1000)


def _traffic_light(ok: bool, warning: bool = False) -> TrafficLight:
    if not ok:
        return "red"
    if warning:
        return "yellow"
    return "green"


def _workflow_views_from_runtime() -> dict[str, Any]:
    views = workflow_views()
    return {
        "deviation_queue": views["deviation_queue"].model_dump(mode="json"),
        "engineering_reliability_board": views["engineering_reliability_board"].model_dump(mode="json"),
        "plant_head_assurance": views["plant_head_assurance"].model_dump(mode="json"),
        "validation_audit_room": views["validation_audit_room"].model_dump(mode="json"),
    }


def _runtime_events() -> list[dict[str, Any]]:
    return [
        {
            "event_id": bundle.event.event_id,
            "site_id": bundle.event.site_id,
            "area_id": bundle.event.area_id,
            "room_id": bundle.event.room_id,
            "asset_id": bundle.event.asset_id,
            "metric": bundle.event.metric,
            "severity": bundle.event.severity,
            "status": bundle.event.status,
            "batch_id": bundle.event.batch_id,
            "product_id": bundle.event.product_id,
            "source_system": bundle.event.source_system,
            "connector_id": bundle.event.connector_id,
        }
        for bundle in demo_event_bundles().values()
    ]


def _connector_source_label(connector_id: str) -> str:
    lower = connector_id.lower()
    if "historian" in lower or "ignition" in lower:
        return "BMS/Historian"
    if "qms" in lower:
        return "QMS"
    if "lims" in lower:
        return "LIMS"
    if "erp" in lower:
        return "ERP"
    if "cmms" in lower:
        return "CMMS"
    return "Industrial Source"


def _build_data_flows(run: EvidenceRun) -> dict[str, Any]:
    connector_replay = run.ingestion.get("connector_replay", {})
    connections: list[dict[str, Any]] = []
    for connector_id, replay in sorted(connector_replay.items()):
        latency_ms = _duration_ms(replay.get("started_at"), replay.get("completed_at"))
        records_out = int(replay.get("records_out", 0))
        replay_ok = replay.get("status") == "success"
        status = "green"
        reason = "Active ingestion; telemetry within expected envelope."
        if not replay_ok:
            status = "red"
            reason = "Connection failed or replay did not complete."
        elif records_out == 0:
            status = "red"
            reason = "No data received from source system."
        elif latency_ms is not None and latency_ms > 1500:
            status = "yellow"
            reason = "Degraded connection with elevated latency."
        elif latency_ms is None:
            status = "yellow"
            reason = "Latency timestamps unavailable; monitor connector health."
        connections.append(
            {
                "source": _connector_source_label(connector_id),
                "target": "Areos Event Backbone",
                "status": status,
                "latency_ms": latency_ms,
                "records_out": records_out,
                "reason": reason,
            }
        )

    downstream = [
        ("Areos Event Backbone", "QA Release Readiness", "Validation artifacts and dossier updates"),
        ("Areos Event Backbone", "Plant Ops Risk View", "Excursion impact and triage signals"),
        ("Areos Event Backbone", "MCP Assistant", "Grounded operational context"),
    ]
    for source, target, reason in downstream:
        connections.append({"source": source, "target": target, "status": "green", "latency_ms": None, "records_out": None, "reason": reason})

    return {
        "pipeline": "automation-pyramid-observability",
        "archetype_hint": "BMS/LIMS/MES/ERP/QMS/CMMS -> Areos -> Persona workflows",
        "connections": connections,
    }


def _build_topology(workflows: dict[str, Any]) -> dict[str, Any]:
    validation_room = workflows.get("validation_audit_room", {})
    missing_by_event = validation_room.get("missing_source_records", {})
    completeness_by_event = validation_room.get("evidence_lineage_completeness", {})
    queue_by_event = {
        item.get("event_id"): item
        for item in workflows.get("deviation_queue", {}).get("queue", [])
        if item.get("event_id")
    }
    assets_by_site: dict[str, dict[str, dict[str, Any]]] = {}

    for event in _runtime_events():
        event_id = event["event_id"]
        queue_item = queue_by_event.get(event_id, {})
        missing_count = int(queue_item.get("missing_evidence_count", len(missing_by_event.get(event_id, []))))
        asset_id = event["asset_id"]
        site_id = event["site_id"]
        area_id = event["area_id"]
        asset = assets_by_site.setdefault(site_id, {}).setdefault(
            asset_id,
            {
                "asset_label": _asset_label(asset_id),
                "domain_path": _domain_path(site_id, area_id, asset_id),
                "site_id": site_id,
                "site_label": _site_label(site_id),
                "area_id": area_id,
                "area_label": _area_label(area_id),
                "room_id": event["room_id"],
                "status": "green",
                "latest_events": [],
                "business_reason": [],
            },
        )
        light = _severity_light(str(event["severity"]), missing_count)
        if light == "red" or asset["status"] != "red" and light == "yellow":
            asset["status"] = light
        asset["latest_events"].append(
            {
                "event_label": _to_title(event_id.replace("event::", "")),
                "severity": event["severity"],
                "metric": _to_title(event["metric"]),
                "batch": event["batch_id"] or "No active batch reference",
                "evidence_completeness": completeness_by_event.get(event_id),
                "owner": queue_item.get("owner", "Unassigned"),
            }
        )
        if missing_count:
            asset["business_reason"].append(f"{missing_count} evidence gap(s) block release decisions")
        if str(event["severity"]).lower() in {"critical", "high"}:
            asset["business_reason"].append(f"{event['severity']} severity quality risk under triage")

    sites = []
    for site_id, assets in sorted(assets_by_site.items()):
        area_groups: dict[str, list[dict[str, Any]]] = {}
        for asset in assets.values():
            area_groups.setdefault(asset["area_id"], []).append(asset)
        areas = []
        for area_id, area_assets in sorted(area_groups.items()):
            areas.append(
                {
                    "area_label": _area_label(area_id),
                    "status": _aggregate_light([asset["status"] for asset in area_assets]),
                    "assets": area_assets,
                }
            )
        sites.append(
            {
                "site_label": _site_label(site_id),
                "site_archetype": ARCHETYPE_BY_SITE.get(site_id, "General Manufacturing"),
                "status": _aggregate_light([asset["status"] for asset in assets.values()]),
                "areas": areas,
            }
        )
    return {
        "source": "Domain abstraction layer over validation artifacts and workflow state",
        "sites": sites,
    }


def _status_counts(topology: dict[str, Any]) -> dict[str, int]:
    counts = {"green": 0, "yellow": 0, "red": 0}
    for site in topology.get("sites", []):
        for area in site.get("areas", []):
            for asset in area.get("assets", []):
                counts[asset["status"]] = counts.get(asset["status"], 0) + 1
    return counts


def _build_readiness(run: EvidenceRun, workflows: dict[str, Any], data_flows: dict[str, Any]) -> dict[str, Any]:
    checks = run.summary.get("checks", {})
    validation_room = workflows.get("validation_audit_room", {})
    completeness_table = validation_room.get("dossier_completeness_table", [])
    package_score = checks.get("package_completeness_score")
    not_audit_ready = sum(
        1 for status in validation_room.get("audit_ready_status", {}).values() if status != "audit_ready"
    )
    connector_validation = run.ingestion.get("connector_validation", {})
    all_valid = bool(connector_validation) and all(item.get("valid") is True for item in connector_validation.values())
    flow_statuses = [flow["status"] for flow in data_flows.get("connections", []) if flow["target"] == "Areos Event Backbone"]
    stages = [
        {
            "stage_label": "System preconditions",
            "status": _traffic_light(bool(run.preconditions), warning=not bool(run.preconditions)),
            "business_summary": "Connector registry, health checks, and enterprise readiness are available.",
        },
        {
            "stage_label": "Pipeline ingestion",
            "status": _traffic_light(all_valid and "red" not in flow_statuses, warning="yellow" in flow_statuses),
            "business_summary": "Data flow from enterprise systems is normalized into the backbone.",
        },
        {
            "stage_label": "Assurance and impact",
            "status": "yellow" if checks.get("state_of_control_outcome") == "BREACH_CONFIRMED" else "green",
            "business_summary": "Excursion and impact logic completed with deterministic outcomes.",
        },
        {
            "stage_label": "Dossier readiness",
            "status": _traffic_light(
                package_score is not None and float(package_score) >= 0.7,
                warning=not_audit_ready > 0,
            ),
            "business_summary": f"Latest dossier completeness is {package_score}; {not_audit_ready} event(s) remain pending audit readiness closure.",
        },
        {
            "stage_label": "Persona workflows",
            "status": _traffic_light(bool(completeness_table), warning=not_audit_ready > 0),
            "business_summary": "Role-specific queues are populated for Admin, QA, and Plant Ops.",
        },
    ]
    return {
        "overall_status": _aggregate_light([stage["status"] for stage in stages]),
        "stages": stages,
    }


def _build_personas(workflows: dict[str, Any], data_flows: dict[str, Any]) -> dict[str, Any]:
    validation_room = workflows.get("validation_audit_room", {})
    deviation_queue = workflows.get("deviation_queue", {}).get("queue", [])
    engineering = workflows.get("engineering_reliability_board", {})
    leadership = workflows.get("plant_head_assurance", {})
    red_or_yellow_flows = [flow for flow in data_flows["connections"] if flow["status"] in {"yellow", "red"}]

    system_admin = {
        "label": "System Administrator",
        "objective": "Topology configuration and system health",
        "kpis": [
            {"name": "Degraded/Broken Data Flows", "value": len(red_or_yellow_flows), "status": _status_badge("red" if any(f["status"] == "red" for f in red_or_yellow_flows) else "yellow" if red_or_yellow_flows else "green")},
            {"name": "Connector Contracts Valid", "value": len([c for c in red_or_yellow_flows if c["target"] == "Areos Event Backbone"]) == 0},
            {"name": "Chronic Assets Flagged", "value": len(engineering.get("chronic_assets", []))},
        ],
        "highlights": [flow["reason"] for flow in red_or_yellow_flows[:5]] or ["All source pipelines are stable."],
        "recommended_actions": [
            "Review connector latency trend and polling retry windows.",
            "Validate site topology template changes before production rollout.",
            "Correlate edge/core heartbeat anomalies with ingestion degradation.",
        ],
    }

    qa = {
        "label": "Quality Assurance (QA)",
        "objective": "Compliance and release readiness",
        "kpis": [
            {"name": "Open Dossier Items", "value": len(validation_room.get("dossier_completeness_table", []))},
            {"name": "Pending Human Approvals", "value": len(validation_room.get("approval_status", {}))},
            {"name": "Not Audit Ready", "value": len([x for x in validation_room.get("audit_ready_status", {}).values() if x != "audit_ready"]), "status": "yellow"},
        ],
        "highlights": [
            f"{row.get('event_id')}: completeness {row.get('completeness_score')}, status {row.get('approval_status')}"
            for row in validation_room.get("dossier_completeness_table", [])[:5]
        ],
        "recommended_actions": [
            "Close missing evidence records before QA disposition.",
            "Prioritize high-severity batch-impacting excursions.",
            "Confirm human approvals before final release decision.",
        ],
    }

    plant_ops = {
        "label": "Plant Head / Plant Ops",
        "objective": "Operational efficiency and risk management",
        "kpis": [
            {"name": "High-Risk Open Events", "value": len(leadership.get("open_high_risk_events", [])), "status": "yellow"},
            {"name": "Batch Release Risks", "value": leadership.get("batch_release_risk_count", 0), "status": "yellow"},
            {"name": "Site Risk Tier", "value": leadership.get("site_risk_tier", "unknown")},
        ],
        "highlights": [leadership.get("executive_summary", "No plant summary available")] + [
            f"{item.get('event_id')} owned by {item.get('owner')}" for item in deviation_queue[:4]
        ],
        "recommended_actions": [
            "Escalate critical equipment issues affecting active batches.",
            "Coordinate QA and Engineering on chronic recurrence hotspots.",
            "Use triage queue to prevent bottlenecks on impacted lines.",
        ],
    }

    personas = {
        "system_admin": system_admin,
        "qa": qa,
        "plant_ops": plant_ops,
        "ops": plant_ops,
        "engineering": system_admin,
        "leadership": plant_ops,
    }
    return personas


def build_control_plane_snapshot(evidence_root: Path | str | None = None) -> dict[str, Any]:
    run = _load_latest_evidence_run(evidence_root)
    workflows = run.workflows or _workflow_views_from_runtime()
    data_flows = _build_data_flows(run)
    topology = _build_topology(workflows)
    readiness = _build_readiness(run, workflows, data_flows)
    personas = _build_personas(workflows, data_flows)
    return {
        "control_plane": {
            "name": "Areos Enterprise Manufacturing Control Plane",
            "mode": "enterprise_read_only_observability",
            "latest_run_status": run.summary.get("status", "no_e2e_artifacts_found"),
            "latest_run_root": str(run.run_root) if run.run_root else None,
        },
        "aws_alignment": {
            "edge_connectivity": "AWS IoT Greengrass",
            "industrial_time_series": "AWS IoT SiteWise",
            "event_ingestion": "AWS IoT Core + Rules Engine",
            "knowledge_backbone": "Aurora/S3/Bedrock Knowledge Base",
        },
        "topology": topology,
        "data_flows": data_flows,
        "readiness": readiness,
        "status_counts": _status_counts(topology),
        "personas": personas,
        "mcp": {
            "status": "ready_for_server_binding",
            "contract": "Assistant reads normalized control-plane views and evidence graph summaries.",
        },
    }


def build_control_plane_assistant_answer(
    query: ControlPlaneAssistantQuery,
    evidence_root: Path | str | None = None,
) -> dict[str, Any]:
    snapshot = build_control_plane_snapshot(evidence_root)
    question = query.question.lower()
    persona_key = query.persona or "plant_ops"
    persona = snapshot["personas"].get(persona_key, snapshot["personas"]["plant_ops"])
    readiness = snapshot["readiness"]
    degraded_flows = [flow for flow in snapshot["data_flows"]["connections"] if flow["status"] in {"yellow", "red"}]

    if "yellow" in question or "status" in question or "why" in question:
        summary = "Yellow indicates the system is running, but at least one risk or evidence closure item needs attention."
        details = [
            f"- **{stage['stage_label']}** is **{stage['status']}**: {stage['business_summary']}"
            for stage in readiness["stages"]
            if stage["status"] == "yellow"
        ] or ["- No yellow stages are active right now."]
    elif "capa" in question or "deviation" in question:
        summary = "CAPA/deviation workflow is active with triage-required events."
        queue = snapshot["personas"]["plant_ops"]["highlights"]
        details = [f"- {item}" for item in queue[:5]]
    elif "dossier" in question or "evidence" in question or "audit" in question:
        summary = "Dossier readiness depends on evidence closure and human approvals."
        details = [f"- {item}" for item in snapshot["personas"]["qa"]["highlights"][:5]]
    elif "flow" in question or "pipeline" in question or "latency" in question:
        summary = "Pipeline telemetry is tracked per integration flow with traffic-light status."
        details = [
            f"- **{flow['source']} -> {flow['target']}** is **{flow['status']}** ({flow['reason']})"
            for flow in degraded_flows[:6]
        ] or ["- All data flows are green within expected latency."]
    else:
        summary = f"{persona['label']} view is active with role-specific actions and KPIs."
        details = [f"- {item}" for item in persona["recommended_actions"]]

    table_rows = [
        [stage["stage_label"], stage["status"], stage["business_summary"]]
        for stage in readiness["stages"]
    ]
    markdown = "\n".join(
        [
            f"### {summary}",
            "",
            "#### Current Guidance",
            *details,
            "",
            "#### Readiness Snapshot",
            "| Workflow Stage | Status | Business Summary |",
            "| --- | --- | --- |",
            *[f"| {row[0]} | {row[1]} | {row[2]} |" for row in table_rows],
            "",
            "#### Next Actions",
            *[f"1. {step}" for step in persona["recommended_actions"][:3]],
        ]
    )

    return {
        "persona": persona["label"],
        "response_format": "markdown",
        "summary": summary,
        "response_markdown": markdown,
        "grounding_sources": [
            snapshot["control_plane"]["latest_run_root"] or "runtime workflow model",
            "normalized control-plane abstraction layer",
            "workflow and evidence summaries",
        ],
        "human_approval_required": True,
    }


def render_control_plane_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Areos Enterprise Control Plane</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #060f1d; color: #dbe9ff; }
    header { padding: 26px 32px; background: linear-gradient(135deg, #0f2540, #1a1f2f); border-bottom: 1px solid #294564; }
    h1, h2, h3 { margin: 0; } h1 { font-size: 28px; } h2 { font-size: 18px; margin-bottom: 12px; }
    .sub { margin-top: 8px; color: #a9bfd8; }
    main { display: grid; grid-template-columns: 1.25fr .95fr; gap: 16px; padding: 18px; }
    section, .card { background: #101c2c; border: 1px solid #243b56; border-radius: 14px; padding: 14px; }
    .grid { display: grid; gap: 12px; } .kpi { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .pill { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 3px 9px; font-size: 12px; text-transform: uppercase; }
    .dot { width: 9px; height: 9px; border-radius: 999px; display: inline-block; }
    .green { background: #0b3a28; color: #a7f3d0; } .yellow { background: #3b320a; color: #fde68a; } .red { background: #3b1212; color: #fecaca; }
    .dot.green { background: #22c55e; } .dot.yellow { background: #facc15; } .dot.red { background: #ef4444; }
    .site { border: 1px solid #2d4d6d; border-radius: 12px; padding: 10px; margin-bottom: 10px; background: #0b1727; }
    .area { border-left: 2px solid #355978; margin-top: 8px; padding-left: 8px; }
    .asset { border-left: 4px solid #16a34a; background: #15263a; border-radius: 8px; padding: 8px; margin-top: 8px; }
    .asset.yellow { border-left-color: #facc15; } .asset.red { border-left-color: #ef4444; }
    .muted { color: #9cb3cc; font-size: 13px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; } th, td { border-bottom: 1px solid #28415f; padding: 8px; text-align: left; vertical-align: top; }
    .tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
    button { background: #203953; color: #dbe9ff; border: 0; border-radius: 8px; padding: 8px 11px; cursor: pointer; }
    button.active { background: #2563eb; }
    input { width: calc(100% - 20px); border: 1px solid #2b4967; border-radius: 8px; padding: 10px; background: #081324; color: #fff; margin-bottom: 8px; }
    #assistant { white-space: pre-wrap; font-size: 14px; line-height: 1.45; background: #0a1423; border-radius: 10px; padding: 10px; }
    @media (max-width: 980px) { main { grid-template-columns: 1fr; } .kpi { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  </style>
</head>
<body>
  <header>
    <h1>Areos Enterprise Manufacturing Control Plane</h1>
    <div class="sub">Domain-driven observability layer over connected manufacturing workflows.</div>
  </header>
  <main>
    <div class="grid">
      <section>
        <h2>Readiness Overview</h2>
        <div id="kpi" class="grid kpi"></div>
        <table id="stageTable"></table>
      </section>
      <section>
        <h2>Manufacturing Topology</h2>
        <div id="topology"></div>
      </section>
      <section>
        <h2>Data Flow Pipeline Observability</h2>
        <table id="flowTable"></table>
      </section>
    </div>
    <div class="grid">
      <section>
        <h2>Role-Based Workflows</h2>
        <div id="personaTabs" class="tabs"></div>
        <div id="personaView"></div>
      </section>
      <section>
        <h2>MCP Assistant</h2>
        <input id="question" value="Why is the system yellow?" />
        <button onclick="askAssistant()">Ask</button>
        <div id="assistant"></div>
      </section>
    </div>
  </main>
  <script>
    let snapshot = null;
    const badge = (status) => `<span class="pill ${status}"><span class="dot ${status}"></span>${status}</span>`;
    const personaKeys = ["system_admin", "qa", "plant_ops"];

    function renderKpi() {
      const c = snapshot.status_counts;
      const cards = [
        ["Run", snapshot.control_plane.latest_run_status],
        ["Overall", snapshot.readiness.overall_status],
        ["Green Assets", c.green],
        ["Yellow/Red Assets", c.yellow + c.red],
      ];
      document.getElementById("kpi").innerHTML = cards.map(([k,v]) => `<div class="card"><h3>${k}</h3><strong>${v}</strong></div>`).join("");
    }

    function renderStages() {
      const rows = snapshot.readiness.stages.map(stage => `<tr><td>${stage.stage_label}</td><td>${badge(stage.status)}</td><td>${stage.business_summary}</td></tr>`).join("");
      document.getElementById("stageTable").innerHTML = `<thead><tr><th>Stage</th><th>Status</th><th>Business Summary</th></tr></thead><tbody>${rows}</tbody>`;
    }

    function renderTopology() {
      document.getElementById("topology").innerHTML = snapshot.topology.sites.map(site => `
        <div class="site"><strong>${site.site_label}</strong> (${site.site_archetype}) ${badge(site.status)}
          ${site.areas.map(area => `<div class="area"><strong>${area.area_label}</strong> ${badge(area.status)}
            ${area.assets.map(asset => `<div class="asset ${asset.status}"><strong>${asset.asset_label}</strong>
              <div class="muted">${asset.domain_path}</div>
              <div class="muted">${asset.business_reason.slice(0,2).join(" · ")}</div>
            </div>`).join("")}
          </div>`).join("")}
        </div>
      `).join("");
    }

    function renderFlows() {
      const rows = snapshot.data_flows.connections.map(flow => `<tr><td>${flow.source}</td><td>${flow.target}</td><td>${badge(flow.status)}</td><td>${flow.latency_ms ?? "n/a"}</td><td>${flow.reason}</td></tr>`).join("");
      document.getElementById("flowTable").innerHTML = `<thead><tr><th>Source</th><th>Target</th><th>Status</th><th>Latency (ms)</th><th>Condition</th></tr></thead><tbody>${rows}</tbody>`;
    }

    function renderPersonaTabs() {
      const tabs = personaKeys.map((key, idx) => `<button class="${idx===0 ? "active" : ""}" onclick="showPersona('${key}', this)">${snapshot.personas[key].label}</button>`).join("");
      document.getElementById("personaTabs").innerHTML = tabs;
      showPersona(personaKeys[0]);
    }

    function showPersona(key, element) {
      document.querySelectorAll("#personaTabs button").forEach(el => el.classList.remove("active"));
      if (element) { element.classList.add("active"); }
      const p = snapshot.personas[key];
      const kpis = p.kpis.map(k => `<li>${k.name}: <strong>${k.value}</strong>${k.status ? " (" + k.status + ")" : ""}</li>`).join("");
      const highlights = p.highlights.map(x => `<li>${x}</li>`).join("");
      const actions = p.recommended_actions.map(x => `<li>${x}</li>`).join("");
      document.getElementById("personaView").innerHTML = `
        <h3>${p.label}</h3>
        <div class="muted">${p.objective}</div>
        <h3 style="margin-top:10px">KPIs</h3><ul>${kpis}</ul>
        <h3>Highlights</h3><ul>${highlights}</ul>
        <h3>Guided Actions</h3><ol>${actions}</ol>`;
    }

    async function askAssistant() {
      const question = document.getElementById("question").value;
      const body = { question: question, persona: "plant_ops" };
      const response = await fetch("/control-plane/api/assistant/query", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
      }).then(r => r.json());
      document.getElementById("assistant").innerText = response.response_markdown;
    }

    async function load() {
      snapshot = await fetch("/control-plane/api/overview").then(r => r.json());
      renderKpi();
      renderStages();
      renderTopology();
      renderFlows();
      renderPersonaTabs();
      askAssistant();
    }
    load();
  </script>
</body>
</html>"""
