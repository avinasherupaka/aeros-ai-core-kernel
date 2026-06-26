# 04 Run Humidity Excursion Demo

The humidity excursion demo is the primary Dendrix scenario. This runbook shows
every way to run it and what to look for.

---

## The scenario

**Plant**: Hyderabad OSD site — Compression Room 1  
**Product**: Hygrostatin 10 mg tablet (hygroscopic)  
**Batch**: BATCH-OSD-2026-001  
**Utility**: AHU-03 (HVAC serving the room)  

**Event sequence**:
| Time (minute) | Relative Humidity | State | Notes |
|---|---|---|---|
| 0–19 | 49.0 %RH | IN_CONTROL | Normal operation |
| 20–41 | 63.0 %RH | ACTION | **22-minute ACTION excursion** |
| 42–59 | 50.0 %RH | IN_CONTROL | AHU restored |

Alert limit: 55 %RH  
Action limit: 60 %RH

**Areos must**: detect the breach, link to active batch/product/room/equipment/utility,
preserve source lineage, and produce a `StateOfControlAssessment` ready for
evidence dossier generation.

---

## Option 1: Print the raw scenario JSON

```bash
python -m aeros.kernel.simulation.humidity_excursion
```

Output shows 60 events. Look for events with `"above_action": true` — you should
find exactly 22 of them.

---

## Option 2: Publish to MQTT (requires broker)

```bash
# Terminal 1
docker compose up mqtt

# Terminal 2
python -m aeros.kernel.ot.mqtt_subscriber

# Terminal 3
python -m aeros.kernel.simulation.humidity_excursion --publish-mqtt
```

Each message on the MQTT topic carries the full Sparkplug-inspired envelope with
tenant/site/asset lineage. In the subscriber terminal, watch for `state=ACTION`
in minutes 20–41.

---

## Option 3: Run via API

```bash
uvicorn aeros.kernel.api.main:app --reload
```

Then:
```bash
# Raw scenario
curl http://localhost:8000/scenario/humidity-excursion | python3 -m json.tool | head -60

# State-of-control assessment
curl http://localhost:8000/state-of-control/humidity-excursion | python3 -m json.tool
```

The `/state-of-control/humidity-excursion` endpoint returns:
```json
{
  "assessment": {
    "assessment_id": "...",
    "tenant_id": "acme_pharma",
    "site_id": "hyd_site_01",
    "area_id": "osd_manufacturing",
    "asset_id": "ahu_03",
    "metric": "relative_humidity",
    "outcome": "BREACH_CONFIRMED",
    "excursion_duration_minutes": 22.0,
    "breach_start": "2026-...",
    "breach_end": "2026-...",
    "action_limit": 60.0,
    "alert_limit": 55.0,
    "peak_value": 63.0,
    "batch_id": "BATCH-OSD-2026-001",
    "product_id": "hygrostatin_10mg_tablet",
    "source_lineage": {...}
  },
  "assurance_events": [
    {
      "event_type": "state_of_control_breach",
      ...
    }
  ]
}
```

---

## Option 4: Run the test suite

```bash
pytest tests/test_humidity_scenario.py tests/test_state_of_control.py -v
```

---

## What to explain to a pharma customer

> "When Compression Room 1 humidity crosses the action limit, Areos immediately:
> 1. Classifies the state (IN_CONTROL / ALERT / ACTION).
> 2. Identifies the active batch, product, room, and equipment.
> 3. Records the excursion duration (22 minutes in this scenario).
> 4. Generates a structured assessment with full source lineage.
> 5. Emits a typed STATE_OF_CONTROL_BREACH event ready for the evidence builder.
>
> The QA reviewer then approves a human-readable evidence pack — they do not need
> to query the BMS, MES, and CMMS separately."
