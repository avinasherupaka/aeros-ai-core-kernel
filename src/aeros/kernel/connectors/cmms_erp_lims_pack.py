from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest
from aeros.kernel.connectors.sdk import BaseConnector


class _FileBackedConnector(BaseConnector):
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


class CMMSConnector(_FileBackedConnector):
    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            self.with_lineage(
                {
                    "record_type": "cmms_work_order",
                    "source_record_id": record["work_order_id"],
                    "work_order_id": record["work_order_id"],
                    "asset_id": record["asset_id"],
                    "completed_at": record["completed_at"],
                    "status": record["status"],
                    "summary": record["summary"],
                }
            )
            for record in records
        ]

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())


class ERPConnector(_FileBackedConnector):
    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            self.with_lineage(
                {
                    "record_type": "erp_batch_genealogy",
                    "source_record_id": record["genealogy_id"],
                    "batch_id": record["batch_id"],
                    "product_id": record["product_id"],
                    "material_lot_id": record["material_lot_id"],
                    "released_at": record["released_at"],
                }
            )
            for record in records
        ]

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())


class LIMSConnector(_FileBackedConnector):
    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            self.with_lineage(
                {
                    "record_type": "lims_result",
                    "source_record_id": record["result_id"],
                    "batch_id": record.get("batch_id"),
                    "sample_id": record["sample_id"],
                    "parameter": record["parameter"],
                    "result": record["result"],
                    "unit": record["unit"],
                    "sampled_at": record["sampled_at"],
                    "status": record["status"],
                }
            )
            for record in records
        ]

    def pull(self) -> list[dict[str, Any]]:
        return self.normalize(self.extract())
