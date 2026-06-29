from aeros.kernel.agents import EngineeringAgent


def test_engineering_agent_returns_hotspots():
    response = EngineeringAgent().ask("Which assets are recurring hotspots?")

    assert "chronic_assets" in response
    assert response["answer"].lower().startswith("recurring hotspots")


def test_engineering_agent_returns_recommended_actions():
    response = EngineeringAgent().ask("What engineering actions are recommended?")

    assert response["recommended_actions"]
