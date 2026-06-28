from aeros.kernel.assurance.event_to_impact import evaluate_event_impact
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.ontology.industry_packs import build_demo_ontology_context, get_scenario_definition


def test_event_to_impact_links_batch_product_and_missing_evidence():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    impact = evaluate_event_impact(
        bundle.event,
        build_demo_ontology_context(bundle.scenario_id),
        get_scenario_definition(bundle.scenario_id),
        available_evidence=["BMS trend", "MES batch record"],
    )
    assert impact.impacted_batch_id == "BATCH-OSD-2026-001"
    assert impact.impacted_product_id == "hygrostatin_10mg_tablet"
    assert "AHU alarm log" in impact.missing_evidence
    assert impact.confidence_score < 0.99
