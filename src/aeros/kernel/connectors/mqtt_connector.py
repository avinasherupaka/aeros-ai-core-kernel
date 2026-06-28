from typing import Any

from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest
from aeros.kernel.connectors.sdk import BaseConnector
from aeros.kernel.ot.mqtt_publisher import MQTTPublisher


class MQTTConnector(BaseConnector):
    def __init__(self, manifest: ConnectorManifest, topic: str, publisher: MQTTPublisher | None = None):
        super().__init__(manifest)
        self.topic = topic
        self.publisher = publisher or MQTTPublisher()

    def health(self) -> ConnectorHealth:
        return ConnectorHealth(
            connector_id=self.manifest.connector_id,
            status="UP",
            details={"topic": self.topic, "host": self.publisher.host, "port": self.publisher.port},
        )

    def pull(self) -> list[dict[str, Any]]:
        return []

    def wrap_for_publish(self, record: dict[str, Any]) -> dict[str, Any]:
        return self.with_lineage(record)
