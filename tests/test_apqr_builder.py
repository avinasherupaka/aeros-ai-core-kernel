from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.dossiers.apqr import build_apqr_section


def test_apqr_builder_summarizes_events_recurrence_and_recommendations():
    bundles = [
        get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression"),
        get_demo_event_bundle("event::api_reactor_temperature_excursion"),
    ]
    section = build_apqr_section(
        site_id="enterprise_demo",
        events=[bundle.event for bundle in bundles],
        impacts=[bundle.impact for bundle in bundles],
        reliability_insights=[bundle.reliability_insight for bundle in bundles],
    )
    assert len(section.utility_environmental_events) == 2
    assert all("severity=" in item for item in section.utility_environmental_events)
    assert section.management_review_recommendations
