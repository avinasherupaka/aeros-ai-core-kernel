"""
Greengrass-style edge gateway for Areos.

Reads measurements from a source (OPC UA server or simulation fallback),
normalises them into SparkplugInspiredEnvelope payloads, and publishes
to the local MQTT UNS broker.

AWS Greengrass equivalent:
  - Greengrass core device runs on-premises
  - OPC UA collector component reads BMS/EMS tags
  - Stream Manager component buffers and forwards to IoT Core MQTT

Local equivalent:
  - This Python service polls the OPC UA simulator (or simulation fallback)
  - Publishes to Mosquitto MQTT broker

Run:
    # Start broker first:
    docker compose up mqtt

    # Optional: start OPC UA sim:
    python -m aeros.kernel.ot.opcua_server_sim

    # Start gateway:
    python -m aeros.kernel.ingestion.edge_gateway
"""

import asyncio
import uuid
from datetime import datetime, timezone

from aeros.kernel.ot.sparkplug_envelope import SparkplugInspiredEnvelope
from aeros.kernel.ot.uns import build_uns_topic


class EdgeGateway:
    """Reads tags from OPC UA (or simulation) and publishes to MQTT UNS."""

    def build_topic(self, tenant: str, site: str, area: str, room: str, asset: str, data_domain: str, metric: str) -> str:
        return build_uns_topic(tenant, site, area, room, asset, data_domain, metric)

    def build_envelope(self, payload: dict) -> SparkplugInspiredEnvelope:
        return SparkplugInspiredEnvelope(**payload)

    def wrap_reading(
        self,
        tenant_id: str,
        site_id: str,
        asset_id: str,
        metric: str,
        value: float,
        unit: str,
        sequence: int = 0,
        source_protocol: str = "opcua",
        source_system: str = "bms",
        quality: str = "GOOD",
    ) -> SparkplugInspiredEnvelope:
        return SparkplugInspiredEnvelope(
            tenant_id=tenant_id,
            site_id=site_id,
            edge_node_id="edge_hyd_01",
            device_id=asset_id,
            metric=metric,
            value=value,
            unit=unit,
            quality=quality,
            sequence=sequence,
            source_protocol=source_protocol,
            source_system=source_system,
            trace_id=str(uuid.uuid4()),
        )


async def run_gateway_loop(
    tenant_id: str = "acme_pharma",
    site_id: str = "hyd_site_01",
    area_id: str = "osd_manufacturing",
    room_id: str = "compression_room_1",
    asset_id: str = "ahu_03",
    mqtt_host: str = "localhost",
    mqtt_port: int = 1883,
    opcua_endpoint: str = "opc.tcp://localhost:4840/freeopcua/server/",
    poll_interval: float = 5.0,
    use_simulation_fallback: bool = False,
) -> None:
    """
    Main gateway loop.

    Tries to connect to the OPC UA server; falls back to simulation data
    if --simulation-fallback flag is set or server is unavailable.
    Publishes to MQTT UNS on every poll cycle.
    """
    from aeros.kernel.ot.mqtt_publisher import MQTTPublisher

    gateway = EdgeGateway()
    publisher = MQTTPublisher(host=mqtt_host, port=mqtt_port)

    topic = gateway.build_topic(tenant_id, site_id, area_id, room_id, asset_id, "utility", "relative_humidity")
    print(f"[edge-gateway] MQTT topic   : {topic}")
    print(f"[edge-gateway] OPC UA source: {opcua_endpoint}")
    print(f"[edge-gateway] Poll interval: {poll_interval}s")
    print("[edge-gateway] Starting loop — press Ctrl-C to stop")

    seq = 0
    sim_minute = 0

    while True:
        try:
            if not use_simulation_fallback:
                from aeros.kernel.ot.opcua_client import browse_and_read_metrics
                readings = await browse_and_read_metrics(opcua_endpoint)
                rh = float(readings.get("RelativeHumidity", 49.0))
                quality = "GOOD"
            else:
                raise RuntimeError("simulation fallback requested")
        except Exception:
            # Fallback to simulation profile
            rh = 63.0 if 20 <= (sim_minute % 60) < 42 else 49.0
            quality = "SIMULATED"
            sim_minute += 1

        envelope = gateway.wrap_reading(
            tenant_id=tenant_id,
            site_id=site_id,
            asset_id=asset_id,
            metric="relative_humidity",
            value=rh,
            unit="%RH",
            sequence=seq,
            quality=quality,
        )

        try:
            publisher.publish(topic, envelope)
            print(f"[edge-gateway] [{datetime.now(timezone.utc).isoformat()}] RH={rh}%  quality={quality}  seq={seq}")
        except Exception as exc:
            print(f"[edge-gateway] MQTT publish failed: {exc} — ensure broker is running: docker compose up mqtt")

        seq += 1
        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Areos edge gateway (Greengrass-style)")
    parser.add_argument("--simulation-fallback", action="store_true", help="Use simulation data instead of OPC UA")
    parser.add_argument("--mqtt-host", default="localhost")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--opcua-endpoint", default="opc.tcp://localhost:4840/freeopcua/server/")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    args = parser.parse_args()

    asyncio.run(
        run_gateway_loop(
            mqtt_host=args.mqtt_host,
            mqtt_port=args.mqtt_port,
            opcua_endpoint=args.opcua_endpoint,
            poll_interval=args.poll_interval,
            use_simulation_fallback=args.simulation_fallback,
        )
    )
