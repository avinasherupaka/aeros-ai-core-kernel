"""Backbone facade: seeds the lakehouse + graph store and exposes status.

On first access it builds the demo event bundles (from the config-driven
scenario library), ingests them into the DuckDB lakehouse (bronze/silver/gold)
and persists each evidence graph into the property-graph store. Subsequent
API calls read from these durable stores. Everything degrades gracefully if
DuckDB is unavailable.
"""

from __future__ import annotations

import threading
from functools import lru_cache
from typing import Any

from aeros.kernel.data_backbone.graph_store import GraphStore
from aeros.kernel.data_backbone.lakehouse import Lakehouse


class Backbone:
    def __init__(self) -> None:
        self.lakehouse = Lakehouse()
        self.graph = GraphStore()
        self.available = self.lakehouse.available and self.graph.available
        self.seeded = False
        self._seed_lock = threading.Lock()
        self.seed_error: str | None = None

    def seed(self) -> None:
        if self.seeded or not self.available:
            return
        with self._seed_lock:
            if self.seeded:
                return
            try:
                # Imported lazily to avoid a heavy import at module load.
                from aeros.kernel.api.demo_data import demo_event_bundles

                for event_id, bundle in demo_event_bundles().items():
                    self.lakehouse.ingest_bundle(bundle)
                    self.graph.upsert_graph(event_id, bundle.evidence_graph)
                self.lakehouse.export_parquet()
                self.seeded = True
            except Exception as exc:  # pragma: no cover
                self.seed_error = str(exc)

    def status(self) -> dict[str, Any]:
        self.seed()
        return {
            "available": self.available,
            "engine": "duckdb",
            "db_path": str(self.lakehouse.db_path),
            "seeded": self.seeded,
            "seed_error": self.seed_error,
            "lakehouse_zones": self.lakehouse.table_counts(),
            "graph": self.graph.stats(),
        }


@lru_cache(maxsize=1)
def get_backbone() -> Backbone:
    backbone = Backbone()
    backbone.seed()
    return backbone
