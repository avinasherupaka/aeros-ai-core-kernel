from aeros.kernel.assurance.event_to_impact import evaluate_event_impact
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.ontology.industry_packs import build_demo_ontology_context, get_scenario_definition


def test_pharma_osd_humidity_has_impact_rationale_and_path():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    impact = evaluate_event_impact(
        bundle.event,
        build_demo_ontology_context(bundle.scenario_id),
        get_scenario_definition(bundle.scenario_id),
        available_evidence=["BMS trend"],
    )
    assert impact.impact_rationale
    assert impact.impact_path is not None
    assert impact.impact_path.event_id == bundle.event.event_id
    assert len(impact.impact_path.path_steps) >= 2


def test_api_reactor_temperature_has_decision_options():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    impact = evaluate_event_impact(
        bundle.event,
        build_demo_ontology_context(bundle.scenario_id),
        get_scenario_definition(bundle.scenario_id),
    )
    assert impact.decision_options


def test_biotech_cold_room_has_evidence_status_list():
    bundle = get_demo_event_bundle("event::biotech_cold_room_temperature_excursion")
    impact = evaluate_event_impact(
        bundle.event,
        build_demo_ontology_context(bundle.scenario_id),
        get_scenario_definition(bundle.scenario_id),
    )
    assert impact.evidence_status_list
    statuses = {e.status for e in impact.evidence_status_list}
    assert statuses <= {"present", "missing", "not_applicable", "needs_human_review"}


def test_risk_severity_scores_present():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    impact = evaluate_event_impact(
        bundle.event,
        build_demo_ontology_context(bundle.scenario_id),
        get_scenario_definition(bundle.scenario_id),
    )
    assert impact.risk_severity_scores
    for score in impact.risk_severity_scores.values():
        assert 0.0 <= score <= 1.0
