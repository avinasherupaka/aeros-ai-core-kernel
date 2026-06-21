from aeros.kernel.simulation.humidity_excursion import generate_humidity_excursion


def test_humidity_excursion_has_22_min_action_limit_breach():
    scenario = generate_humidity_excursion()
    above_action = [e for e in scenario["events"] if e["above_action"]]
    assert len(above_action) == 22
    assert scenario["excursion_duration_minutes"] == 22


def test_humidity_scenario_includes_supporting_records():
    scenario = generate_humidity_excursion()
    assert "prior_similar_deviation" in scenario["supporting_records"]
    assert "recent_maintenance" in scenario["supporting_records"]
