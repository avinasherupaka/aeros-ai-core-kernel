import csv
import json
from pathlib import Path
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest
from aeros.kernel.connectors.sdk import BaseConnector


class FileImportConnector(BaseConnector):
    def __init__(self, manifest: ConnectorManifest, file_path: str):
        super().__init__(manifest)
        self.file_path = Path(file_path)

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            connector_id=self.manifest.connector_id,
            status="UP" if self.file_path.exists() else "DOWN",
            details={"file_path": str(self.file_path)},
        )

    def pull(self) -> list[dict[str, Any]]:
        suffix = self.file_path.suffix.lower()
        if suffix == ".json":
            payload = json.loads(self.file_path.read_text())
            records = payload if isinstance(payload, list) else [payload]
        elif suffix == ".csv":
            with self.file_path.open("r", newline="") as f:
                records = list(csv.DictReader(f))
        else:
            raise ValueError(f"Unsupported file type: {self.file_path.suffix}")

        return [self.with_lineage(record) for record in records]
