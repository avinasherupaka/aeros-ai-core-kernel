import networkx as nx


class NetworkXGraphAdapter:
    """Initial local adapter; production target is Amazon Neptune-backed implementation."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_entity(self, entity_id: str, entity_type: str, **attrs) -> None:
        self.graph.add_node(entity_id, entity_type=entity_type, **attrs)

    def add_relationship(self, source_id: str, relationship: str, target_id: str, **attrs) -> None:
        self.graph.add_edge(source_id, target_id, key=relationship, relationship=relationship, **attrs)

    def relationship_types(self) -> set[str]:
        return {edge_data["relationship"] for _, _, edge_data in self.graph.edges(data=True)}
