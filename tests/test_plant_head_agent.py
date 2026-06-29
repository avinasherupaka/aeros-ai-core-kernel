from aeros.kernel.agents import PlantHeadAgent


def test_plant_head_agent_summarizes_top_risks():
    response = PlantHeadAgent().ask("What are the top site risks?")

    assert response["site_risk_tier"] in {"low", "medium", "high", "critical"}
    assert response["action_priorities"]
