import pytest

from aeros.kernel.api.main import control_plane_overview, control_plane_persona, control_plane_ui
from aeros.kernel.control_plane import ControlPlaneAssistantQuery
from aeros.kernel.control_plane.service import build_control_plane_assistant_answer, build_control_plane_snapshot
from aeros.kernel.simulation.e2e_magic_suite import run_magic_e2e_suite


@pytest.fixture(scope="module")
def evidence_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("control-plane-evidence")
    run_magic_e2e_suite(output_root=root, max_replay_records=2)
    return root


def test_control_plane_normalizes_latest_e2e_artifacts(evidence_root):
    snapshot = build_control_plane_snapshot(evidence_root=evidence_root)

    assert snapshot["control_plane"]["latest_run_status"] == "passed"
    assert snapshot["control_plane"]["mode"] == "enterprise_read_only_observability"
    assert "AWS IoT SiteWise" in snapshot["aws_alignment"]["industrial_time_series"]
    assert "AWS IoT Greengrass" in snapshot["aws_alignment"]["edge_connectivity"]
    assert snapshot["topology"]["sites"]
    first_asset = snapshot["topology"]["sites"][0]["areas"][0]["assets"][0]
    assert "domain_path" in first_asset
    assert "sitewise::" not in first_asset["domain_path"]
    assert snapshot["readiness"]["overall_status"] in {"green", "yellow", "red"}
    assert {"system_admin", "qa", "plant_ops"} <= set(snapshot["personas"])
    assert snapshot["data_flows"]["connections"]


def test_control_plane_readiness_exposes_reason_codes(evidence_root):
    stages = build_control_plane_snapshot(evidence_root=evidence_root)["readiness"]["stages"]

    assert {stage["stage_label"] for stage in stages} == {
        "System preconditions",
        "Pipeline ingestion",
        "Assurance and impact",
        "Dossier readiness",
        "Persona workflows",
    }
    assert all(stage["business_summary"] for stage in stages)


def test_control_plane_assistant_is_grounded_in_normalized_context(evidence_root):
    answer = build_control_plane_assistant_answer(
        ControlPlaneAssistantQuery(question="Why is the system yellow?", persona="qa"),
        evidence_root=evidence_root,
    )

    assert "Yellow indicates" in answer["summary"]
    assert "#### Readiness Snapshot" in answer["response_markdown"]
    assert "| Workflow Stage | Status | Business Summary |" in answer["response_markdown"]
    assert answer["human_approval_required"] is True
    assert answer["response_format"] == "markdown"


def test_control_plane_api_and_ui_are_available():
    overview = control_plane_overview()
    ui = control_plane_ui()
    persona = control_plane_persona("qa")

    assert overview["control_plane"]["name"] == "Areos Enterprise Manufacturing Control Plane"
    assert "Areos Enterprise Manufacturing Control Plane" in ui
    assert persona["label"] == "Quality Assurance (QA)"
