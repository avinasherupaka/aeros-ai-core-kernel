from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aeros.kernel.assurance.evidence_graph import EvidenceGraphSnapshot


@dataclass
class PropertyGraphNodeRecord:
    node_id: str
    labels: list[str]
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class PropertyGraphEdgeRecord:
    edge_id: str  # "{source_id}__{edge_type}__{target_id}"
    source_id: str
    target_id: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


def project_evidence_graph_to_property_records(
    snapshot: EvidenceGraphSnapshot,
) -> tuple[list[PropertyGraphNodeRecord], list[PropertyGraphEdgeRecord]]:
    """Convert in-memory evidence graph snapshot to Neptune-ready property graph records."""
    nodes = [
        PropertyGraphNodeRecord(
            node_id=n.node_id,
            labels=[n.node_type.value],
            properties={"label": n.label, **n.attributes},
        )
        for n in snapshot.nodes
    ]
    edges = [
        PropertyGraphEdgeRecord(
            edge_id=f"{e.source_id}__{e.edge_type.value}__{e.target_id}",
            source_id=e.source_id,
            target_id=e.target_id,
            label=e.edge_type.value,
            properties=e.attributes,
        )
        for e in snapshot.edges
    ]
    return nodes, edges
