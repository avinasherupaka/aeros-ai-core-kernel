from aeros.kernel.api.demo_data import get_demo_event_bundle


def test_evidence_graph_contains_event_batch_risk_and_evidence_nodes():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    node_ids = {node.node_id for node in bundle.evidence_graph.nodes}
    edge_types = {edge.edge_type.value for edge in bundle.evidence_graph.edges}
    assert bundle.event.event_id in node_ids
    assert bundle.event.batch_id in node_ids
    assert any(node.node_type.value == "Risk" for node in bundle.evidence_graph.nodes)
    assert "EVIDENCED_BY" in edge_types
    assert "HAS_RISK" in edge_types
