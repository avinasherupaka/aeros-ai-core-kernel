import json
from pathlib import Path

from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier


def test_full_package_creates_all_files(tmp_path):
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
        output_root=tmp_path,
    )
    assert Path(dossier.markdown_path).exists()
    assert Path(dossier.json_path).exists()
    assert Path(dossier.manifest_path).exists()
    assert Path(dossier.evidence_index_path).exists()
    assert Path(dossier.source_citations_path).exists()
    assert Path(dossier.missing_evidence_checklist_path).exists()
    assert Path(dossier.approval_placeholder_path).exists()
    assert Path(dossier.package_hashes_path).exists()


def test_manifest_contains_expected_keys(tmp_path):
    bundle = get_demo_event_bundle("event::biotech_cold_room_temperature_excursion")
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
        output_root=tmp_path,
    )
    manifest = json.loads(Path(dossier.manifest_path).read_text())
    assert "package_id" in manifest
    assert "artifacts" in manifest
    assert len(manifest["artifacts"]) >= 6
    assert "compliance_note" in manifest


def test_package_hashes_sha256(tmp_path):
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
        output_root=tmp_path,
    )
    hashes = json.loads(Path(dossier.package_hashes_path).read_text())
    assert hashes["algorithm"] == "sha256"
    assert "dossier.md" in hashes["hashes"]
    assert len(hashes["hashes"]["dossier.md"]) == 64


def test_package_completeness_score(tmp_path):
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
        output_root=tmp_path,
    )
    assert 0.0 <= dossier.package_completeness_score <= 1.0


def test_approval_placeholder_has_required_fields(tmp_path):
    bundle = get_demo_event_bundle("event::biotech_cold_room_temperature_excursion")
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
        output_root=tmp_path,
    )
    approval = json.loads(Path(dossier.approval_placeholder_path).read_text())
    assert approval["status"] == "pending_human_approval"
    assert "electronic_signature_placeholder" in approval
    assert "compliance_note" in approval


def test_source_citations_present(tmp_path):
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    dossier = build_gmp_dossier(
        event=bundle.event,
        assessment=bundle.assessment,
        impact_assessment=bundle.impact,
        evidence_graph=bundle.evidence_graph,
        reliability_insight=bundle.reliability_insight,
        output_root=tmp_path,
    )
    citations = json.loads(Path(dossier.source_citations_path).read_text())
    assert "citations" in citations
    assert citations["citations"]
    assert "source_system" in citations["citations"][0]
