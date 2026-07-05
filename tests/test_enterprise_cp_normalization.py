"""Tests domain-safe normalization and infrastructure masking for the enterprise control plane."""

from __future__ import annotations

import pytest

from aeros.kernel.connectors.registry import default_connector_registry
from aeros.kernel.control_plane.service import SITE_LABELS, build_control_plane_snapshot
from aeros.kernel.simulation.e2e_magic_suite import run_magic_e2e_suite


@pytest.fixture(scope="module")
def evidence_root(tmp_path_factory: pytest.TempPathFactory):
    root = tmp_path_factory.mktemp("enterprise-cp-normalization")
    run_magic_e2e_suite(output_root=root, max_replay_records=2)
    return root


def _asset_domain_paths(snapshot: dict) -> list[str]:
    return [
        asset["domain_path"]
        for site in snapshot["topology"]["sites"]
        for area in site["areas"]
        for asset in area["assets"]
    ]


@pytest.mark.parametrize("forbidden_pattern", ["sitewise::", "arn:aws:", "iot-core::", "connector_id:"])
def test_no_infra_tokens_in_site_health_cards(evidence_root, forbidden_pattern: str):
    snapshot = build_control_plane_snapshot(evidence_root=evidence_root)
    domain_paths = _asset_domain_paths(snapshot)

    assert domain_paths
    assert all(forbidden_pattern not in path for path in domain_paths)

    try:
        from aeros.kernel.control_plane.models import validate_no_infra_leak
    except (ImportError, ModuleNotFoundError):
        return

    assert validate_no_infra_leak(snapshot["topology"]) == []


def test_site_labels_are_domain_safe(evidence_root):
    snapshot = build_control_plane_snapshot(evidence_root=evidence_root)
    site_labels = {site["site_label"] for site in snapshot["topology"]["sites"]}

    assert "Hyderabad Plant 1" in site_labels
    assert "Bengaluru Biopharma Campus" in site_labels
    assert "hyd_site_01" not in site_labels
    assert "blr_bio_01" not in site_labels


def test_connector_labels_use_domain_names(evidence_root):
    raw_health = default_connector_registry().health()
    snapshot = build_control_plane_snapshot(evidence_root=evidence_root)

    raw_ids = {item["connector_id"] for item in raw_health}
    normalized_sources = {flow["source"] for flow in snapshot["data_flows"]["connections"]}
    normalized_text = " ".join(sorted(normalized_sources))

    assert "qms-veeva-vault-live" in raw_ids
    assert "historian-ignition-live" in raw_ids
    assert "QMS" in normalized_sources
    assert "BMS/Historian" in normalized_sources
    assert "qms-veeva-vault-live" not in normalized_text
    assert "historian-ignition-live" not in normalized_text


def test_token_translation_coverage():
    assert {"hyd_site_01", "blr_bio_01"} <= set(SITE_LABELS)


def test_asset_path_has_no_raw_ids(evidence_root):
    snapshot = build_control_plane_snapshot(evidence_root=evidence_root)

    assert all("::" not in path for path in _asset_domain_paths(snapshot))


def test_readiness_never_silent_green_for_missing(tmp_path_factory: pytest.TempPathFactory):
    empty_root = tmp_path_factory.mktemp("enterprise-cp-empty")
    snapshot = build_control_plane_snapshot(evidence_root=empty_root)

    assert snapshot["control_plane"]["latest_run_status"] == "no_e2e_artifacts_found"
    assert snapshot["readiness"]["overall_status"] != "green"
