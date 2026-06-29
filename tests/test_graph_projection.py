from aeros.kernel.assurance.evidence_graph import (
    EvidenceGraphSnapshot, EvidenceNode, EvidenceEdge,
    EvidenceNodeType, EvidenceEdgeType,
)
from aeros.kernel.data_backbone.graph_projection import (
    project_evidence_graph_to_property_records,
    PropertyGraphNodeRecord,
    PropertyGraphEdgeRecord,
)


def _make_snapshot():
    return EvidenceGraphSnapshot(
        nodes=[
            EvidenceNode(node_id='EVT-001', node_type=EvidenceNodeType.EVENT, label='humidity_excursion'),
            EvidenceNode(node_id='BATCH-001', node_type=EvidenceNodeType.BATCH, label='B-2024-001'),
            EvidenceNode(node_id='ASSET-001', node_type=EvidenceNodeType.EQUIPMENT, label='HVAC-01'),
        ],
        edges=[
            EvidenceEdge(source_id='EVT-001', target_id='BATCH-001', edge_type=EvidenceEdgeType.ACTIVE_DURING),
            EvidenceEdge(source_id='EVT-001', target_id='ASSET-001', edge_type=EvidenceEdgeType.DERIVED_FROM),
        ],
    )


def test_node_count():
    snapshot = _make_snapshot()
    nodes, edges = project_evidence_graph_to_property_records(snapshot)
    assert len(nodes) == 3


def test_edge_count():
    snapshot = _make_snapshot()
    nodes, edges = project_evidence_graph_to_property_records(snapshot)
    assert len(edges) == 2


def test_node_labels_match_type():
    snapshot = _make_snapshot()
    nodes, _ = project_evidence_graph_to_property_records(snapshot)
    event_node = next(n for n in nodes if n.node_id == 'EVT-001')
    assert 'Event' in event_node.labels


def test_edge_id_format():
    snapshot = _make_snapshot()
    _, edges = project_evidence_graph_to_property_records(snapshot)
    edge = next(e for e in edges if e.source_id == 'EVT-001' and e.target_id == 'BATCH-001')
    assert 'ACTIVE_DURING' in edge.edge_id


def test_empty_snapshot():
    snapshot = EvidenceGraphSnapshot()
    nodes, edges = project_evidence_graph_to_property_records(snapshot)
    assert nodes == []
    assert edges == []
