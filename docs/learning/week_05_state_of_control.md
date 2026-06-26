# Week 05 — Canonical Model and State-of-Control Engine

## Learning goal

Understand how raw measurements become typed assurance events, how the
state-of-control engine evaluates streams, and how the event router dispatches
results to downstream consumers.

---

## What is "state of control"?

In GMP manufacturing, **state of control** means that all critical process
parameters (CPPs) and critical quality attributes (CQAs) are within their
validated limits. When a parameter exceeds an action limit, the process is
considered **out of state of control** and a quality investigation may be required.

This is not just monitoring — it is the formal GMP determination that governs
whether a batch can proceed, be released, or must be investigated.

Areos automates the detection and documentation of state-of-control breaches.
Humans still approve the quality decision.

---

## Canonical event model

Raw measurements (OPC UA tags, BMS values, MQTT messages) are first normalized
into `CanonicalEvent` objects. Then, after state-of-control evaluation, typed
`AssuranceEvent` objects are produced.

```
Raw RH tag (63.0 %RH)
  → CanonicalEvent (event_type="measurement", payload=raw)
    → MeasurementReading (structured, stored in registry)
      → StateOfControlAssessment (outcome=BREACH_CONFIRMED, excursion=22 min)
        → AssuranceEvent (event_type=STATE_OF_CONTROL_BREACH)
          → EventRouter → evidence builder / dossier generator
```

### `StateOfControlAssessment`

```python
StateOfControlAssessment(
    assessment_id="uuid-...",
    tenant_id="acme_pharma",
    site_id="hyd_site_01",
    area_id="osd_manufacturing",
    asset_id="ahu_03",
    metric="relative_humidity",
    outcome=AssessmentOutcome.BREACH_CONFIRMED,
    excursion_duration_minutes=22.0,
    breach_start=datetime(2026, 1, 1, 8, 20, ...),
    breach_end=datetime(2026, 1, 1, 8, 41, ...),
    action_limit=60.0,
    alert_limit=55.0,
    peak_value=63.0,
    batch_id="BATCH-OSD-2026-001",
    product_id="hygrostatin_10mg_tablet",
    source_lineage={
        "tenant_id": "acme_pharma",
        "site_id": "hyd_site_01",
        "area_id": "osd_manufacturing",
        "asset_id": "ahu_03",
        "source_system": "bms_simulation",
    },
)
```

The `source_lineage` dict is the audit trail — it records where the data came from.

### Assessment outcomes

| Outcome | Meaning |
|---|---|
| `IN_CONTROL` | All readings within limits |
| `ALERT` | Some readings above alert limit, none above action limit |
| `ACTION_REQUIRED` | Reserved for future use |
| `BREACH_CONFIRMED` | One or more readings above action limit |

---

## State-of-control engine

`src/aeros/kernel/assurance/state_of_control.py`

```python
from aeros.kernel.assurance.state_of_control import (
    run_humidity_state_of_control,
    build_assurance_events_from_assessment,
)

assessment = run_humidity_state_of_control(
    readings=readings,
    tenant_id="acme_pharma",
    site_id="hyd_site_01",
    area_id="osd_manufacturing",
    asset_id="ahu_03",
    alert_limit=55.0,
    action_limit=60.0,
    batch_id="BATCH-OSD-2026-001",
    product_id="hygrostatin_10mg_tablet",
)

events = build_assurance_events_from_assessment(assessment)
# events[0].event_type == EventType.STATE_OF_CONTROL_BREACH
```

Engine logic:
1. Count readings above action_limit → excursion_duration_minutes.
2. If > 0 → BREACH_CONFIRMED.
3. Else if any above alert_limit → ALERT.
4. Else → IN_CONTROL.

---

## Event router (IoT Rules Engine equivalent)

`src/aeros/kernel/ingestion/event_router.py`

AWS IoT Rules Engine routes MQTT messages to Lambda, SQS, S3, EventBridge based
on SQL-like rules. The local `EventRouter` routes `AssuranceEvent` objects to
Python callables based on event_type.

```python
from aeros.kernel.ingestion.event_router import EventRouter, RoutingRule
from aeros.kernel.models.canonical import EventType

captured = []
router = EventRouter()

# Rule 1: log all events
router.register_rule(RoutingRule(
    rule_id="log_all",
    event_type_filter="*",
    handler=lambda e: print(f"EVENT: {e.event_type}"),
))

# Rule 2: route breaches to evidence builder (future)
router.register_rule(RoutingRule(
    rule_id="breach_to_evidence",
    event_type_filter=EventType.STATE_OF_CONTROL_BREACH.value,
    handler=lambda e: captured.append(e),
))

router.route_many(events)
```

---

## Evidence source model

`src/aeros/kernel/models/evidence.py`

`EvidenceSource` records the provenance of each data point used in an assessment:

```python
EvidenceSource(
    source_id="uuid-...",
    tenant_id="acme_pharma",
    site_id="hyd_site_01",
    source_type=EvidenceSourceType.BMS,
    system_name="BMS Compression Room 1",
    asset_id="ahu_03",
    metric="relative_humidity",
    value=63.0,
    unit="%RH",
    timestamp=datetime(...),
    topic="areos/acme_pharma/.../relative_humidity",
    trace_id="uuid-...",
    quality="GOOD",
    read_only=True,  # Areos never writes back
)
```

---

## API endpoint

```bash
curl http://localhost:8000/state-of-control/humidity-excursion
```

Returns:
```json
{
  "assessment": {
    "outcome": "BREACH_CONFIRMED",
    "excursion_duration_minutes": 22.0,
    ...
  },
  "assurance_events": [
    {"event_type": "state_of_control_breach", ...}
  ]
}
```

---

## Run / test

```bash
pytest tests/test_state_of_control.py -v
```

18 tests covering:
- All three outcomes (BREACH_CONFIRMED, ALERT, IN_CONTROL)
- Empty readings edge case
- Source lineage preservation
- Batch/product linkage
- AssuranceEvent generation
- EventRouter routing (wildcard, specific, non-matching)

---

## AWS equivalent

| Local | AWS |
|---|---|
| `run_humidity_state_of_control()` | Lambda / Step Functions state machine |
| `StateOfControlAssessment` | Step Functions output / DynamoDB record |
| `AssuranceEvent` | EventBridge event / SNS message |
| `EventRouter` | IoT Rules Engine rule + actions |
| `EvidenceSource` | S3 object + Neptune provenance node |

---

## What happens next (Weeks 6–10)

- **Week 6**: Event-to-impact engine — link breach to batch/product quality risk.
- **Week 7**: Evidence graph builder — Neptune-like graph of event→batch→evidence relationships.
- **Week 8**: GMP dossier builder — human-readable evidence packs from the graph.
- **Week 9**: APQR/deviation workflow integration.
- **Week 10**: Control plane personas and Bedrock agent integration.
