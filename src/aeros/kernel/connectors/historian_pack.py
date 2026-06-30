from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest, ConnectorReplayRequest, ConnectorRunResult
from aeros.kernel.connectors.sdk import BaseConnector


class HistorianConnector(BaseConnector):
    def __init__(
        self,
        manifest: ConnectorManifest,
        dataset_path: str,
        *,
        live_api_base_url: str = "",
        live_api_path: str = "",
    ):
        super().__init__(manifest)
        self.dataset_path = Path(dataset_path)
        self.live_api_base_url = live_api_base_url.rstrip("/")
        self.live_api_path = live_api_path or "/api/v1/tags/history"

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            connector_id=self.manifest.connector_id,
            status="UP" if self.dataset_path.exists() or self.live_api_base_url else "DOWN",
            details={
                "dataset_path": str(self.dataset_path),
                "pack": self.manifest.pack_name,
                "live_api_base_url": self.live_api_base_url,
                "live_mode_enabled": bool(self.live_api_base_url),
            },
        )

    def extract(self) -> list[dict[str, Any]]:
        payload = json.loads(self.dataset_path.read_text())
        records = payload if isinstance(payload, list) else [payload]
        if not self.live_api_base_url:
            return records
        return [
            {
                **record,
                "ingestion_source": "live_api",
                "api_endpoint": f"{self.live_api_base_url}{self.live_api_path}",
            }
            for record in records
        ]

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
