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
