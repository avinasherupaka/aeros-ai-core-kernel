from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest, ConnectorReplayRequest, ConnectorRunResult
from aeros.kernel.connectors.sdk import BaseConnector


class HistorianConnector(BaseConnector):
    def __init__(self, manifest: ConnectorManifest, dataset_path: str):
        super().__init__(manifest)
        self.dataset_path = Path(dataset_path)

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            connector_id=self.manifest.connector_id,
            status="UP" if self.dataset_path.exists() else "DOWN",
            details={"dataset_path": str(self.dataset_path), "pack": self.manifest.pack_name},
        )

    def extract(self) -> list[dict[str, Any]]:
        payload = json.loads(self.dataset_path.read_text())
        return payload if isinstance(payload, list) else [payload]

    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized = []
        for record in records:
            normalized.append(
                self.with_lineage(
                    {
                        "record_type": "parameter_observation",
                        "source_record_id": record["record_id"],
                        "tag": record["tag"],
                        "asset_id": record["asset_id"],
                        "observed_at": record["timestamp"],
                        "value": record["value"],
                        "unit": record["unit"],
                    }
                )
            )
        return normalized

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())

    def discover(self) -> dict[str, Any]:
        records = self.extract()
        return {
            **super().discover(),
            "tag_count": len({record["tag"] for record in records}),
            "asset_ids": sorted({record["asset_id"] for record in records}),
        }

    def replay(self, request: ConnectorReplayRequest) -> ConnectorRunResult:
        source_records = self._filter_by_time_window(self.extract(), request)
        normalized = self.normalize(source_records)
        return ConnectorRunResult(
            connector_id=self.manifest.connector_id,
            run_type="replay",
            status="success",
            records_in=len(source_records),
            records_out=len(normalized),
            details={"dataset_path": str(self.dataset_path)},
            sample_output=normalized[:5],
        )
