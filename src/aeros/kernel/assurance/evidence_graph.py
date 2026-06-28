from __future__ import annotations

from enum import Enum
from typing import Any

import networkx as nx
from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.assurance.reliability_intelligence import ReliabilityInsight
from aeros.kernel.models.canonical import AssuranceEvent
from aeros.kernel.ontology.core import OntologyContext


class EvidenceNodeType(str, Enum):
    EVENT = "Event"
    BATCH = "Batch"
    PRODUCT = "Product"
    MATERIAL_LOT = "MaterialLot"
    ROOM = "Room"
    EQUIPMENT = "Equipment"
    UTILITY_SYSTEM = "UtilitySystem"
    SENSOR = "Sensor"
    SOP_CLAUSE = "SOPClause"
    DEVIATION = "Deviation"
    CAPA = "CAPA"
    WORK_ORDER = "WorkOrder"
    LAB_RESULT = "LabResult"
    EVIDENCE_ITEM = "EvidenceItem"
    HUMAN_REVIEW = "HumanReview"
    APPROVAL = "Approval"
    RISK = "Risk"


class EvidenceEdgeType(str, Enum):
    OCCURRED_IN = "OCCURRED_IN"
    ACTIVE_DURING = "ACTIVE_DURING"
    IMPACTS = "IMPACTS"
    EVIDENCED_BY = "EVIDENCED_BY"
    REFERENCES = "REFERENCES"
    SIMILAR_TO = "SIMILAR_TO"
    MAINTAINED_BY = "MAINTAINED_BY"
    CONTROLLED_BY = "CONTROLLED_BY"
    HAS_RISK = "HAS_RISK"
    REVIEWED_BY = "REVIEWED_BY"
    APPROVED_BY = "APPROVED_BY"
    DERIVED_FROM = "DERIVED_FROM"


class EvidenceNode(BaseModel):
    node_id: str
    node_type: EvidenceNodeType
    label: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class EvidenceEdge(BaseModel):
    source_id: str
    target_id: str
    edge_type: EvidenceEdgeType
    attributes: dict[str, Any] = Field(default_factory=dict)


class EvidenceGraphSnapshot(BaseModel):
    nodes: list[EvidenceNode] = Field(default_factory=list)
    edges: list[EvidenceEdge] = Field(default_factory=list)


class InMemoryEvidenceGraph:
    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: EvidenceNode) -> None:
        self.graph.add_node(node.node_id, node_type=node.node_type.value, label=node.label, **node.attributes)

    def add_edge(self, edge: EvidenceEdge) -> None:
        self.graph.add_edge(edge.source_id, edge.target_id, edge_type=edge.edge_type.value, **edge.attributes)

    def snapshot(self) -> EvidenceGraphSnapshot:
        nodes = [
            EvidenceNode(
                node_id=node_id,
                node_type=EvidenceNodeType(data["node_type"]),
                label=data["label"],
                attributes={key: value for key, value in data.items() if key not in {"node_type", "label"}},
            )
            for node_id, data in self.graph.nodes(data=True)
        ]
        edges = [
            EvidenceEdge(
                source_id=source,
                target_id=target,
                edge_type=EvidenceEdgeType(data["edge_type"]),
                attributes={key: value for key, value in data.items() if key != "edge_type"},
            )
            for source, target, _key, data in self.graph.edges(keys=True, data=True)
        ]
        return EvidenceGraphSnapshot(nodes=nodes, edges=edges)

    def get_event_evidence(self, event_id: str) -> list[EvidenceNode]:
        result = []
        for source, target, _key, data in self.graph.edges(keys=True, data=True):
            if source == event_id and data.get("edge_type") == EvidenceEdgeType.EVIDENCED_BY.value:
                node_data = self.graph.nodes[target]
                result.append(EvidenceNode(
                    node_id=target,
                    node_type=EvidenceNodeType(node_data["node_type"]),
                    label=node_data["label"],
                    attributes={k: v for k, v in node_data.items() if k not in {"node_type", "label"}},
                ))
        return result

    def get_impacted_entities(self, event_id: str) -> list[EvidenceNode]:
        impact_edge_types = {EvidenceEdgeType.IMPACTS.value, EvidenceEdgeType.ACTIVE_DURING.value}
        result = []
        for source, target, _key, data in self.graph.edges(keys=True, data=True):
            if source == event_id and data.get("edge_type") in impact_edge_types:
                node_data = self.graph.nodes[target]
                result.append(EvidenceNode(
                    node_id=target,
                    node_type=EvidenceNodeType(node_data["node_type"]),
                    label=node_data["label"],
                    attributes={k: v for k, v in node_data.items() if k not in {"node_type", "label"}},
                ))
        return result

    def get_risks(self, event_id: str) -> list[EvidenceNode]:
        result = []
        for source, target, _key, data in self.graph.edges(keys=True, data=True):
            if source == event_id and data.get("edge_type") == EvidenceEdgeType.HAS_RISK.value:
                node_data = self.graph.nodes[target]
                result.append(EvidenceNode(
                    node_id=target,
                    node_type=EvidenceNodeType(node_data["node_type"]),
                    label=node_data["label"],
                    attributes={k: v for k, v in node_data.items() if k not in {"node_type", "label"}},
                ))
        return result

    def get_missing_evidence(self, event_id: str, required_evidence: list[str]) -> list[str]:
        present_labels = {node.label for node in self.get_event_evidence(event_id)}
        return [item for item in required_evidence if item not in present_labels]

    def get_lineage_path(self, event_id: str) -> list[dict]:
        path = []
        if event_id not in self.graph.nodes:
            return path
        path.append({"node_id": event_id, "node_type": "Event", "label": self.graph.nodes[event_id].get("label", event_id)})
        for source, target, _key, data in self.graph.edges(keys=True, data=True):
            if source == event_id:
                node_data = self.graph.nodes[target]
                path.append({"node_id": target, "node_type": node_data.get("node_type", ""), "label": node_data.get("label", target), "edge_type": data.get("edge_type", "")})
        return path

    def to_neptune_like_triples(self) -> list[dict]:
        triples = []
        for source, target, _key, data in self.graph.edges(keys=True, data=True):
            triples.append({
                "subject": source,
                "predicate": data.get("edge_type", "RELATED_TO"),
                "object": target,
                "subject_type": self.graph.nodes[source].get("node_type", ""),
                "object_type": self.graph.nodes[target].get("node_type", ""),
            })
        return triples


class EvidenceGraphQuery:
    def __init__(self, snapshot: EvidenceGraphSnapshot) -> None:
        self._nodes = {node.node_id: node for node in snapshot.nodes}
        self._edges = snapshot.edges

    def get_neighbors(self, node_id: str, edge_type: EvidenceEdgeType | None = None) -> list[EvidenceNode]:
        targets = [
            edge.target_id for edge in self._edges
            if edge.source_id == node_id and (edge_type is None or edge.edge_type == edge_type)
        ]
        return [self._nodes[t] for t in targets if t in self._nodes]

    def get_event_evidence(self, event_id: str) -> list[EvidenceNode]:
        return self.get_neighbors(event_id, EvidenceEdgeType.EVIDENCED_BY)

    def get_impacted_entities(self, event_id: str) -> list[EvidenceNode]:
        return self.get_neighbors(event_id, EvidenceEdgeType.IMPACTS) + self.get_neighbors(event_id, EvidenceEdgeType.ACTIVE_DURING)

    def get_risks(self, event_id: str) -> list[EvidenceNode]:
        return self.get_neighbors(event_id, EvidenceEdgeType.HAS_RISK)

    def get_missing_evidence(self, event_id: str, required_evidence: list[str]) -> list[str]:
        present = {node.label for node in self.get_event_evidence(event_id)}
        return [item for item in required_evidence if item not in present]

    def get_lineage_path(self, event_id: str) -> list[dict]:
        path = []
        if event_id not in self._nodes:
            return path
        node = self._nodes[event_id]
        path.append({"node_id": event_id, "node_type": node.node_type.value, "label": node.label})
        for edge in self._edges:
            if edge.source_id == event_id:
                target = self._nodes.get(edge.target_id)
                if target:
                    path.append({"node_id": target.node_id, "node_type": target.node_type.value, "label": target.label, "edge_type": edge.edge_type.value})
        return path

    def to_neptune_like_triples(self) -> list[dict]:
        result = []
        for edge in self._edges:
            src = self._nodes.get(edge.source_id)
            tgt = self._nodes.get(edge.target_id)
            result.append({
                "subject": edge.source_id,
                "predicate": edge.edge_type.value,
                "object": edge.target_id,
                "subject_type": src.node_type.value if src else "",
                "object_type": tgt.node_type.value if tgt else "",
            })
        return result


def query_snapshot(snapshot: EvidenceGraphSnapshot) -> EvidenceGraphQuery:
    return EvidenceGraphQuery(snapshot)


def build_evidence_graph(
    event: AssuranceEvent,
    ontology_context: OntologyContext,
    impact_assessment: ImpactAssessment,
    *,
    evidence_items: list[str] | None = None,
    reliability_insight: ReliabilityInsight | None = None,
) -> EvidenceGraphSnapshot:
    graph = InMemoryEvidenceGraph()
    graph.add_node(EvidenceNode(node_id=event.event_id, node_type=EvidenceNodeType.EVENT, label=event.metric, attributes={"severity": event.severity, "event_type": event.event_type.value}))
    graph.add_node(EvidenceNode(node_id=event.asset_id, node_type=EvidenceNodeType.EQUIPMENT, label=event.asset_id))
    graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=event.asset_id, edge_type=EvidenceEdgeType.DERIVED_FROM))

    if event.room_id:
        graph.add_node(EvidenceNode(node_id=event.room_id, node_type=EvidenceNodeType.ROOM, label=event.room_id))
        graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=event.room_id, edge_type=EvidenceEdgeType.OCCURRED_IN))
    if event.batch_id:
        graph.add_node(EvidenceNode(node_id=event.batch_id, node_type=EvidenceNodeType.BATCH, label=event.batch_id))
        graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=event.batch_id, edge_type=EvidenceEdgeType.ACTIVE_DURING))
    if event.product_id:
        graph.add_node(EvidenceNode(node_id=event.product_id, node_type=EvidenceNodeType.PRODUCT, label=event.product_id))
        graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=event.product_id, edge_type=EvidenceEdgeType.IMPACTS))
    if event.material_lot_id:
        graph.add_node(EvidenceNode(node_id=event.material_lot_id, node_type=EvidenceNodeType.MATERIAL_LOT, label=event.material_lot_id))
        graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=event.material_lot_id, edge_type=EvidenceEdgeType.IMPACTS))

    for risk in impact_assessment.likely_quality_risks:
        risk_id = risk.lower().replace(" ", "_")
        graph.add_node(EvidenceNode(node_id=risk_id, node_type=EvidenceNodeType.RISK, label=risk))
        graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=risk_id, edge_type=EvidenceEdgeType.HAS_RISK))

    for evidence in evidence_items or impact_assessment.required_evidence:
        evidence_id = f"evidence::{evidence.lower().replace(' ', '_')}"
        graph.add_node(EvidenceNode(node_id=evidence_id, node_type=EvidenceNodeType.EVIDENCE_ITEM, label=evidence))
        graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=evidence_id, edge_type=EvidenceEdgeType.EVIDENCED_BY))

    review_id = f"review::{event.event_id}"
    approval_id = f"approval::{event.event_id}"
    graph.add_node(EvidenceNode(node_id=review_id, node_type=EvidenceNodeType.HUMAN_REVIEW, label="Human review placeholder"))
    graph.add_node(EvidenceNode(node_id=approval_id, node_type=EvidenceNodeType.APPROVAL, label="Approval placeholder"))
    graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=review_id, edge_type=EvidenceEdgeType.REVIEWED_BY))
    graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=approval_id, edge_type=EvidenceEdgeType.APPROVED_BY))

    if reliability_insight:
        for similar_event_id in reliability_insight.similar_event_ids:
            graph.add_node(EvidenceNode(node_id=similar_event_id, node_type=EvidenceNodeType.EVENT, label="Similar event"))
            graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=similar_event_id, edge_type=EvidenceEdgeType.SIMILAR_TO))
        if reliability_insight.maintenance_context:
            work_order_id = reliability_insight.maintenance_context.split(": ", 1)[0]
            graph.add_node(EvidenceNode(node_id=work_order_id, node_type=EvidenceNodeType.WORK_ORDER, label=work_order_id, attributes={"summary": reliability_insight.maintenance_context}))
            graph.add_edge(EvidenceEdge(source_id=event.asset_id, target_id=work_order_id, edge_type=EvidenceEdgeType.MAINTAINED_BY))

    for relationship in ontology_context.relationships:
        if relationship.target_type == "UtilitySystem":
            graph.add_node(EvidenceNode(node_id=relationship.target_id, node_type=EvidenceNodeType.UTILITY_SYSTEM, label=relationship.target_id))
            graph.add_edge(EvidenceEdge(source_id=event.event_id, target_id=relationship.target_id, edge_type=EvidenceEdgeType.CONTROLLED_BY))

    return graph.snapshot()
