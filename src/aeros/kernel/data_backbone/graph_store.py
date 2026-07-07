"""Persistent property-graph store for the Aeros evidence graph.

A real, queryable property graph backed by DuckDB (nodes + edges tables) with
recursive-CTE lineage traversal. This replaces the previous per-request,
in-memory-only NetworkX graph with a durable store that can answer lineage and
neighbourhood questions across sessions. NetworkX is still used to *build* each
snapshot; here we *persist and query* it.

Uses the same DuckDB file as the lakehouse (a dedicated ``graph`` schema).
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional

try:
    import duckdb  # type: ignore

    _DUCKDB_AVAILABLE = True
except Exception:  # pragma: no cover
    duckdb = None  # type: ignore
    _DUCKDB_AVAILABLE = False

from aeros.kernel.data_backbone.lakehouse import resolve_backbone_dir


class GraphStore:
    """DuckDB-backed property graph with lineage traversal."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.available = _DUCKDB_AVAILABLE
        self._lock = threading.RLock()
        self.db_path = db_path or (resolve_backbone_dir() / "aeros.duckdb")
        self._con = None
        if self.available:
            self._con = duckdb.connect(str(self.db_path))
            self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            c = self._con
            c.execute("CREATE SCHEMA IF NOT EXISTS graph")
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS graph.nodes (
                    node_id VARCHAR, event_id VARCHAR, node_type VARCHAR,
                    label VARCHAR, attributes JSON,
                    PRIMARY KEY (node_id, event_id)
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS graph.edges (
                    source_id VARCHAR, target_id VARCHAR, edge_type VARCHAR,
                    event_id VARCHAR
                )
                """
            )

    def upsert_graph(self, event_id: str, snapshot: Any) -> None:
        """Persist an EvidenceGraphSnapshot for one event."""
        if not self.available:
            return
        with self._lock:
            c = self._con
            c.execute("DELETE FROM graph.nodes WHERE event_id = ?", [event_id])
            c.execute("DELETE FROM graph.edges WHERE event_id = ?", [event_id])
            for node in snapshot.nodes:
                node_type = getattr(node.node_type, "value", str(node.node_type))
                c.execute(
                    "INSERT INTO graph.nodes (node_id, event_id, node_type, label, attributes) VALUES (?,?,?,?,?)",
                    [node.node_id, event_id, node_type, node.label or node.node_id, json.dumps(node.attributes or {})],
                )
            for edge in snapshot.edges:
                edge_type = getattr(edge.edge_type, "value", str(edge.edge_type))
                c.execute(
                    "INSERT INTO graph.edges (source_id, target_id, edge_type, event_id) VALUES (?,?,?,?)",
                    [edge.source_id, edge.target_id, edge_type, event_id],
                )

    def _rows(self, sql: str, params: Optional[list] = None) -> list[dict]:
        with self._lock:
            cur = self._con.execute(sql, params or [])
            columns = [d[0] for d in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def neighbors(self, node_id: str, event_id: Optional[str] = None) -> dict[str, list[dict]]:
        """Return inbound + outbound neighbours of a node."""
        if not self.available:
            return {"outbound": [], "inbound": []}
        clause = "AND event_id = ?" if event_id else ""
        base = [node_id] + ([event_id] if event_id else [])
        outbound = self._rows(
            f"SELECT target_id AS node_id, edge_type FROM graph.edges WHERE source_id = ? {clause}", base
        )
        inbound = self._rows(
            f"SELECT source_id AS node_id, edge_type FROM graph.edges WHERE target_id = ? {clause}", base
        )
        return {"outbound": outbound, "inbound": inbound}

    def lineage(self, node_id: str, event_id: Optional[str] = None, max_depth: int = 8) -> list[dict]:
        """Recursive-CTE downstream lineage traversal from a node."""
        if not self.available:
            return []
        clause = "AND e.event_id = ?" if event_id else ""
        params = [node_id] + ([event_id] if event_id else [])
        sql = f"""
        WITH RECURSIVE lineage(source_id, target_id, edge_type, depth) AS (
            SELECT e.source_id, e.target_id, e.edge_type, 1 AS depth
            FROM graph.edges e
            WHERE e.source_id = ? {clause}
            UNION ALL
            SELECT e.source_id, e.target_id, e.edge_type, l.depth + 1
            FROM graph.edges e
            JOIN lineage l ON e.source_id = l.target_id
            WHERE l.depth < {int(max_depth)}
        )
        SELECT DISTINCT source_id, target_id, edge_type, depth FROM lineage ORDER BY depth
        """
        return self._rows(sql, params)

    def subgraph(self, event_id: str) -> dict[str, list[dict]]:
        """Return the full persisted node/edge set for an event."""
        if not self.available:
            return {"nodes": [], "edges": []}
        nodes = self._rows(
            "SELECT node_id, node_type, label, attributes FROM graph.nodes WHERE event_id = ?", [event_id]
        )
        for node in nodes:
            try:
                node["attributes"] = json.loads(node.get("attributes") or "{}")
            except Exception:
                node["attributes"] = {}
        edges = self._rows(
            "SELECT source_id, target_id, edge_type FROM graph.edges WHERE event_id = ?", [event_id]
        )
        return {"nodes": nodes, "edges": edges}

    def stats(self) -> dict[str, Any]:
        if not self.available:
            return {"available": False, "node_count": 0, "edge_count": 0, "node_types": {}, "edge_types": {}}
        node_count = self._rows("SELECT count(*) AS n FROM graph.nodes")[0]["n"]
        edge_count = self._rows("SELECT count(*) AS n FROM graph.edges")[0]["n"]
        node_types = {r["node_type"]: r["n"] for r in self._rows(
            "SELECT node_type, count(*) AS n FROM graph.nodes GROUP BY node_type ORDER BY n DESC")}
        edge_types = {r["edge_type"]: r["n"] for r in self._rows(
            "SELECT edge_type, count(*) AS n FROM graph.edges GROUP BY edge_type ORDER BY n DESC")}
        return {
            "available": True,
            "node_count": int(node_count),
            "edge_count": int(edge_count),
            "node_types": node_types,
            "edge_types": edge_types,
        }
