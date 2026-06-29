from aeros.kernel.agents import AgentOrchestrator


def test_agent_orchestrator_routes_to_qa():
    response = AgentOrchestrator().ask("Can I close this deviation?")

    assert response["routed_persona"] == "qa"


def test_agent_orchestrator_routes_to_engineering():
    response = AgentOrchestrator().ask("What engineering actions are recommended?")

    assert response["routed_persona"] == "engineering"
