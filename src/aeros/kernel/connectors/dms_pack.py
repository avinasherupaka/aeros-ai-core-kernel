from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest
from aeros.kernel.connectors.sdk import BaseConnector


class DocumentumConnector(BaseConnector):
    def __init__(self, manifest: ConnectorManifest, dataset_path: str, *, live_api_base_url: str = "", live_api_path: str = "/d2/api/documents"):
        super().__init__(manifest)
        self.dataset_path = Path(dataset_path)
        self.live_api_base_url = live_api_base_url.rstrip("/")
        self.live_api_path = live_api_path

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
        return [
            self.with_lineage(
                {
                    "record_type": "dms_document",
                    "source_record_id": record["document_id"],
                    "document_id": record["document_id"],
                    "title": record["title"],
                    "document_type": record.get("document_type", "GxP"),
                    "status": record["status"],
                    "effective_at": record.get("effective_at"),
                }
            )
            for record in records
        ]

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())
