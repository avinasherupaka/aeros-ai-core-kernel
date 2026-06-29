from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest
from aeros.kernel.connectors.sdk import BaseConnector


class _FileBackedConnector(BaseConnector):
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


class QMSConnector(_FileBackedConnector):
    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            self.with_lineage(
                {
                    "record_type": "qms_quality_record",
                    "source_record_id": record["deviation_id"],
                    "deviation_id": record["deviation_id"],
                    "quality_record_type": record["record_type"],
                    "status": record["status"],
                    "batch_id": record.get("batch_id"),
                    "site_id": record.get("site_id", self.manifest.site_id),
                    "event_time": record["opened_at"],
                    "summary": record["summary"],
                }
            )
            for record in records
        ]

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())


class MESConnector(_FileBackedConnector):
    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            self.with_lineage(
                {
                    "record_type": "mes_batch_timeline",
                    "source_record_id": record["timeline_id"],
                    "batch_id": record["batch_id"],
                    "product_id": record["product_id"],
                    "phase": record["phase"],
                    "operation": record["operation"],
                    "event_time": record["timestamp"],
                    "status": record["status"],
                }
            )
            for record in records
        ]

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())
