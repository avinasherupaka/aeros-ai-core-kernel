from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from aeros.kernel.data_backbone.bronze_silver_gold import bronze_path
from aeros.kernel.ingestion.realtime_contracts import SourceSystemEvent


class LocalBronzeWriter:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def write_source_event(self, event: SourceSystemEvent, fingerprint: str) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        relative = bronze_path(event.tenant_id, event.site_id, event.source_system.lower(), "raw_source_records", date_str)
        dir_path = self.root_dir / relative
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{event.event_id}.json"
        file_path.write_text(
            json.dumps(
                {
                    "event_id": event.event_id,
                    "fingerprint": fingerprint,
                    "source_system": event.source_system,
                    "source_type": event.source_type.value,
                    "timestamp": event.timestamp,
                    "parameter": event.parameter,
                    "value": event.value,
                    "unit": event.unit,
                    "raw_payload": event.raw_payload,
                },
                indent=2,
            )
        )
        return str(file_path)


class S3BronzeWriter:
    def __init__(self, bucket_name: str, *, region_name: str = "ap-south-1"):
        try:
            import boto3  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("boto3 is required for S3BronzeWriter") from exc
        self.bucket_name = bucket_name
        self._s3 = boto3.client("s3", region_name=region_name)

    def write_source_event(self, event: SourceSystemEvent, fingerprint: str) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key_prefix = bronze_path(event.tenant_id, event.site_id, event.source_system.lower(), "raw_source_records", date_str)
        key = f"{key_prefix}{event.event_id}.json"
        body = json.dumps(
            {
                "event_id": event.event_id,
                "fingerprint": fingerprint,
                "source_system": event.source_system,
                "source_type": event.source_type.value,
                "timestamp": event.timestamp,
                "parameter": event.parameter,
                "value": event.value,
                "unit": event.unit,
                "raw_payload": event.raw_payload,
            }
        )
        self._s3.put_object(Bucket=self.bucket_name, Key=key, Body=body.encode("utf-8"), ContentType="application/json")
        return f"s3://{self.bucket_name}/{key}"
