import json
from pathlib import Path

from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.dossiers.apqr import build_apqr_section


def _get_bundles():
    return [
        get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression"),
        get_demo_event_bundle("event::api_reactor_temperature_excursion"),
    ]


def test_apqr_event_table_structure():
    bundles = _get_bundles()
    section = build_apqr_section(
        site_id="enterprise_demo",
        events=[b.event for b in bundles],
        impacts=[b.impact for b in bundles],
        reliability_insights=[b.reliability_insight for b in bundles],
    )
    assert len(section.event_table) == 2
    assert "event_id" in section.event_table[0]
    assert "severity" in section.event_table[0]


def test_apqr_risk_themes():
    bundles = _get_bundles()
    section = build_apqr_section(
        site_id="enterprise_demo",
        events=[b.event for b in bundles],
        impacts=[b.impact for b in bundles],
        reliability_insights=[b.reliability_insight for b in bundles],
    )
    assert section.risk_themes


def test_apqr_human_review_statement():
    bundles = _get_bundles()
    section = build_apqr_section(
        site_id="enterprise_demo",
        events=[b.event for b in bundles],
        impacts=[b.impact for b in bundles],
        reliability_insights=[b.reliability_insight for b in bundles],
    )
    assert "human" in section.human_review_statement.lower()


def test_apqr_file_output(tmp_path):
    bundles = _get_bundles()
    section = build_apqr_section(
        site_id="enterprise_demo",
        events=[b.event for b in bundles],
        impacts=[b.impact for b in bundles],
        reliability_insights=[b.reliability_insight for b in bundles],
        period="2026-H1",
        output_root=tmp_path,
    )
    assert section.markdown_path
    assert section.json_path
    assert Path(section.markdown_path).exists()
    assert Path(section.json_path).exists()
    data = json.loads(Path(section.json_path).read_text())
    assert "site_id" in data
