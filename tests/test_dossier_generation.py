from pathlib import Path

from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier


def test_gmp_dossier_writes_markdown_and_json(tmp_path):
    bundle = get_demo_event_bundle("event::biotech_cold_room_temperature_excursion")
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
    markdown = Path(dossier.markdown_path).read_text()
    assert "Human-approved, audit-ready evidence pack" in markdown
    assert "Designed to support 21 CFR Part 11 / GxP controls" in markdown
