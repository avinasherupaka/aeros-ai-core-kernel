from aeros.kernel.assurance.state_of_control import (
    ParameterLimits,
    build_demo_observations_from_scenario,
    build_state_of_control_rules_from_scenario,
    evaluate_state_of_control,
)
from aeros.kernel.ontology.industry_packs import get_scenario_definition


def test_pharma_pressure_cascade_failure_is_breach_confirmed():
    scenario = get_scenario_definition("pharma_osd_pressure_cascade_failure_dispensing")
    observations = build_demo_observations_from_scenario(scenario)
    assessment = evaluate_state_of_control(
        observations=observations,
        parameter_limits=build_state_of_control_rules_from_scenario(scenario),
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="dispensing",
        asset_id="ahu_dispensing_01",
        room_id="dispensing_airlock",
        batch_id="BATCH-OSD-2026-014",
        product_id="apirox_5mg_capsule",
        scenario_id=scenario.scenario_id,
    )
    assert assessment.outcome.value == "BREACH_CONFIRMED"
    assert assessment.severity == "critical"
    assert assessment.excursion_duration_minutes == 7.0


def test_cold_room_temperature_rule_preserves_confidence_and_limits():
    scenario = get_scenario_definition("biotech_cold_room_temperature_excursion")
    observations = build_demo_observations_from_scenario(scenario)
    assessment = evaluate_state_of_control(
        observations=observations,
        parameter_limits=build_state_of_control_rules_from_scenario(scenario),
        tenant_id="bio_enterprise",
        site_id="blr_bio_01",
        area_id="cold_storage",
        asset_id="cold_room_01",
        room_id="cold_room_01",
        scenario_id=scenario.scenario_id,
    )
    assert assessment.confidence >= 0.9
    assert assessment.validated_range == {"min_value": 2.0, "max_value": 8.0}
    assert assessment.parameter_assessments[0]["parameter"] == "cold_room_temperature"


def test_multi_parameter_assessment_uses_highest_severity():
    observations = [
        *build_demo_observations_from_scenario(get_scenario_definition("pharma_osd_humidity_excursion_compression")),
        *build_demo_observations_from_scenario(get_scenario_definition("pharma_osd_pressure_cascade_failure_dispensing")),
    ]
    rules = [
        *build_state_of_control_rules_from_scenario(get_scenario_definition("pharma_osd_humidity_excursion_compression")),
        *build_state_of_control_rules_from_scenario(get_scenario_definition("pharma_osd_pressure_cascade_failure_dispensing")),
    ]
    assessment = evaluate_state_of_control(
        observations=observations,
        parameter_limits=rules,
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        asset_id="ahu_03",
        room_id="compression_room_1",
        scenario_id="combined_test",
    )
    assert assessment.outcome.value == "BREACH_CONFIRMED"
    assert assessment.severity == "critical"
    assert len(assessment.parameter_assessments) == 2
