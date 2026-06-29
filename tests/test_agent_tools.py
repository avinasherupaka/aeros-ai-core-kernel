from aeros.kernel.agents import AgentToolRegistry


def test_agent_tool_registry_exposes_required_tools():
    registry = AgentToolRegistry()

    tools = registry.list_tools()
    health = registry.get_connector_health()

    assert any(tool["name"] == "get_event" for tool in tools)
    assert any(item["connector_id"] == "historian-aveva-pi" for item in health)
