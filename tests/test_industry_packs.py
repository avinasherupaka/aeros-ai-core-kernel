from aeros.kernel.ontology.industry_packs import get_scenario_definition, list_industry_packs, load_scenario_library


REQUIRED_SCENARIOS = {
    "pharma_osd_humidity_excursion_compression",
    "pharma_osd_pressure_cascade_failure_dispensing",
    "pharma_osd_compressed_air_dew_point_excursion",
    "api_reactor_temperature_excursion",
    "api_nitrogen_blanketing_pressure_drop",
    "biotech_bioreactor_ph_excursion",
    "biotech_wfi_conductivity_trend",
    "biotech_cold_room_temperature_excursion",
    "food_allergen_cross_contact_risk",
    "advanced_materials_dry_room_humidity_excursion",
}


def test_industry_packs_list_required_scenarios():
    packs = list_industry_packs()
    scenario_ids = {scenario_id for pack in packs for scenario_id in pack["scenario_ids"]}
    assert REQUIRED_SCENARIOS.issubset(scenario_ids)


def test_scenario_definition_is_data_driven():
    scenario = get_scenario_definition("api_reactor_temperature_excursion")
    assert scenario.industry == "api_chemical"
    assert "SCADA" in scenario.source_systems
    assert "reactor_temperature" in scenario.sample_limits
    assert scenario.evidence_checklist


def test_library_contains_multiple_industry_packs():
    packs = load_scenario_library()
    assert len(packs) >= 4
