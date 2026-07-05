"""Tests readiness scoring and traffic-light rollups for the enterprise control plane."""

from __future__ import annotations

import pytest

from aeros.kernel.control_plane.service import (
    _aggregate_light,
    _severity_light,
    build_control_plane_snapshot,
)
from aeros.kernel.simulation.e2e_magic_suite import run_magic_e2e_suite


@pytest.fixture(scope="module")
def evidence_root(tmp_path_factory: pytest.TempPathFactory):
    root = tmp_path_factory.mktemp("enterprise-cp-readiness")
    run_magic_e2e_suite(output_root=root, max_replay_records=2)
    return root


@pytest.fixture(scope="module")
def readiness_snapshot(evidence_root):
    return build_control_plane_snapshot(evidence_root=evidence_root)["readiness"]


def test_readiness_stages_all_have_reason_codes(readiness_snapshot):
    stages = readiness_snapshot["stages"]

    assert stages
    assert all(stage["business_summary"].strip() for stage in stages)


def test_readiness_traffic_lights_are_valid(readiness_snapshot):
    valid_lights = {"green", "yellow", "red"}
    stage_statuses = {stage["status"] for stage in readiness_snapshot["stages"]}

    assert readiness_snapshot["overall_status"] in valid_lights
    assert stage_statuses <= valid_lights


def test_readiness_has_required_dimensions(readiness_snapshot):
    stage_labels = {stage["stage_label"] for stage in readiness_snapshot["stages"]}

    assert {
        "System preconditions",
        "Pipeline ingestion",
        "Assurance and impact",
        "Dossier readiness",
        "Persona workflows",
    } <= stage_labels


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (["green", "green"], "green"),
        (["green", "yellow"], "yellow"),
        (["green", "red"], "red"),
        (["yellow", "red"], "red"),
    ],
)
def test_rollup_aggregation_respects_worst_case(statuses: list[str], expected: str):
    assert _aggregate_light(statuses) == expected


@pytest.mark.parametrize(
    ("severity", "missing_evidence_count", "expected"),
    [
        ("critical", 0, "red"),
        ("high", 0, "yellow"),
        ("medium", 1, "yellow"),
        ("low", 0, "green"),
    ],
)
def test_severity_light_logic(severity: str, missing_evidence_count: int, expected: str):
    assert _severity_light(severity, missing_evidence_count) == expected


def test_readiness_overall_status_in_valid_set(readiness_snapshot):
    assert readiness_snapshot["overall_status"] in {"green", "yellow", "red"}
