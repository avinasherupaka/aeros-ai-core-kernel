from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest


class BaseConnector(ABC):
    def __init__(self, manifest: ConnectorManifest):
        self.manifest = manifest

    @abstractmethod
    def health(self) -> ConnectorHealth:
        raise NotImplementedError

    @abstractmethod
    def pull(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def with_lineage(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "tenant_id": self.manifest.tenant_id,
            "site_id": self.manifest.site_id,
            "connector_id": self.manifest.connector_id,
            "connector_type": self.manifest.connector_type,
            "source_system": self.manifest.source_system,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "record": record,
        }
