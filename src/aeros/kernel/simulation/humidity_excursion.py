"""
Dendrix humidity excursion scenario simulation.

Simulates 60 minutes of relative-humidity readings in a GMP compression room.
Minutes 20-41 (inclusive) represent a 22-minute ACTION-limit excursion above 60 %RH.
This is the primary demo scenario for Dendrix by Areos.

Run directly (print JSON):
    python -m aeros.kernel.simulation.humidity_excursion

Publish to local MQTT broker:
    python -m aeros.kernel.simulation.humidity_excursion --publish-mqtt

The broker must be running:
    docker compose up mqtt
"""

from datetime import datetime, timedelta, timezone

from aeros.kernel.simulation.plant_topology import build_osd_topology


def generate_humidity_excursion(start_time: datetime | None = None) -> dict:
    base_time = start_time or datetime.now(timezone.utc)
    topology = build_osd_topology()

    alert_limit = 55.0
    action_limit = 60.0
    events = []

    for minute in range(60):
        ts = base_time + timedelta(minutes=minute)
        if minute < 20:
            rh = 49.0
        elif 20 <= minute < 42:
            rh = 63.0
        else:
            rh = 50.0

        events.append(
            {
                "timestamp": ts.isoformat(),
                "metric": "relative_humidity",
                "value": rh,
                "unit": "%RH",
                "above_alert": rh > alert_limit,
                "above_action": rh > action_limit,
                "batch_id": topology["batch"]["batch_id"],
                "product_id": topology["batch"]["product_id"],
                "room_id": topology["room"]["room_id"],
                "utility_asset": topology["utility_asset"]["equipment_id"],
                "equipment": topology["equipment"]["equipment_id"],
                "operation": "compression",
                "operation_active": True,
                "ahu_alarm_active": 20 <= minute < 42,
            }
        )

    supporting_records = {
        "prior_similar_deviation": {
            "deviation_id": "DEV-2025-117",
            "summary": "Compression room humidity action-limit excursion linked to AHU filter blockage.",
        },
        "recent_maintenance": {
            "work_order_id": "CMMS-WO-88421",
            "summary": "AHU-03 preventive maintenance completed 5 days ago (belt tension and filter replacement).",
        },
    }

    return {
        "scenario": "dendrix_humidity_excursion",
        "topology": topology,
        "limits": {"alert_limit": alert_limit, "action_limit": action_limit},
        "excursion_duration_minutes": 22,
        "events": events,
        "supporting_records": supporting_records,
    }


if __name__ == "__main__":
    import argparse
    import json
    import uuid

    parser = argparse.ArgumentParser(description="Dendrix humidity excursion simulation")
    parser.add_argument("--publish-mqtt", action="store_true", help="Publish events to local MQTT broker")
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT broker host (default: localhost)")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT broker port (default: 1883)")
    args = parser.parse_args()

    scenario = generate_humidity_excursion()
    topology = scenario["topology"]

    if args.publish_mqtt:
        from aeros.kernel.ot.mqtt_publisher import MQTTPublisher
        from aeros.kernel.ot.sparkplug_envelope import SparkplugInspiredEnvelope
        from aeros.kernel.ot.uns import build_uns_topic

        topic = build_uns_topic(
            tenant=topology["tenant_id"],
            site=topology["site"]["site_id"],
            area=topology["area"]["area_id"],
            work_center_or_room=topology["room"]["room_id"],
            asset=topology["utility_asset"]["equipment_id"],
            data_domain="utility",
            metric="relative_humidity",
        )
        print(f"[publish-mqtt] Topic : {topic}")
        print(f"[publish-mqtt] Broker: {args.mqtt_host}:{args.mqtt_port}")
        print(f"[publish-mqtt] Events: {len(scenario['events'])}")

        envelopes = []
        for i, event in enumerate(scenario["events"]):
            envelopes.append(
                SparkplugInspiredEnvelope(
                    tenant_id=topology["tenant_id"],
                    site_id=topology["site"]["site_id"],
                    edge_node_id="edge_hyd_01",
                    device_id=topology["utility_asset"]["equipment_id"],
                    metric="relative_humidity",
                    value=event["value"],
                    unit=event["unit"],
                    quality="GOOD",
                    sequence=i,
                    source_protocol="simulated",
                    source_system="bms",
                    trace_id=str(uuid.uuid4()),
                )
            )

        publisher = MQTTPublisher(host=args.mqtt_host, port=args.mqtt_port)
        publisher.publish_many(topic, envelopes)

        for event in scenario["events"]:
            flag = "ACTION" if event["above_action"] else ("ALERT" if event["above_alert"] else "OK")
            print(f"  [{event['timestamp']}] RH={event['value']:5.1f}%RH  state={flag}")

        print(f"\n[publish-mqtt] Done — {len(envelopes)} messages published.")
    else:
        print(json.dumps(scenario, indent=2, default=str))
