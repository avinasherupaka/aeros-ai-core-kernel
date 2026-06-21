from aeros.kernel.ot.sparkplug_envelope import SparkplugInspiredEnvelope
from aeros.kernel.ot.uns import build_uns_topic


class EdgeGateway:
    def build_topic(self, tenant: str, site: str, area: str, room: str, asset: str, data_domain: str, metric: str) -> str:
        return build_uns_topic(tenant, site, area, room, asset, data_domain, metric)

    def build_envelope(self, payload: dict) -> SparkplugInspiredEnvelope:
        return SparkplugInspiredEnvelope(**payload)
