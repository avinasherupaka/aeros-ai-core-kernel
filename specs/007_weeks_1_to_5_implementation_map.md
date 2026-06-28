# 007 Weeks 1–5 Implementation Map

This spec describes what was implemented in this PR and how to navigate it.

---

## What this PR covers

This PR implements a coherent local MVP foundation covering Weeks 1–5 of the
Areos AWS-native kernel build roadmap. It is both a **learning workspace** and
a **working runnable codebase**.

---

## What was implemented

### Week 1 — Domain model and plant topology

| File | What it does |
|---|---|
| `src/aeros/kernel/standards/isa95.py` | ISA-95 hierarchy: Enterprise, Site, Area, Room, Equipment (with GMP fields) |
| `src/aeros/kernel/standards/isa88.py` | ISA-88 batch model: Procedure, Operation, Phase, BatchRecord (with area/room/equipment links) |
| `src/aeros/kernel/models/asset.py` | AssetContext — lightweight asset reference |
| `src/aeros/kernel/models/utility.py` | UtilityReading + UtilityLimits |
| `src/aeros/kernel/simulation/plant_topology.py` | OSD plant topology builder + `__main__` |
| `src/aeros/kernel/simulation/humidity_excursion.py` | 60-event humidity scenario + `--publish-mqtt` flag |

### Week 2 — Unified Namespace and MQTT

| File | What it does |
|---|---|
| `src/aeros/kernel/ot/uns.py` | ISA-95 UNS topic builder with segment sanitization |
| `src/aeros/kernel/ot/sparkplug_envelope.py` | Sparkplug-inspired message envelope with lineage fields |
| `src/aeros/kernel/ot/mqtt_publisher.py` | Single + batch MQTT publish |
| `src/aeros/kernel/ot/mqtt_subscriber.py` | MQTT subscriber with connect/print loop |

### Week 3 — OPC UA and edge gateway

| File | What it does |
|---|---|
| `src/aeros/kernel/ot/opcua_server_sim.py` | asyncua OPC UA server simulating compression room metrics |
| `src/aeros/kernel/ot/opcua_client.py` | Browse + read OPC UA node values |
| `src/aeros/kernel/ingestion/edge_gateway.py` | EdgeGateway class + async poll loop with OPC UA / simulation fallback |
| `src/aeros/kernel/ingestion/normalizer.py` | normalize_measurement: raw dict → CanonicalEvent |

### Week 4 — Local SiteWise-like model

| File | What it does |
|---|---|
| `src/aeros/kernel/storage/local_sitewise.py` | AssetModel, Asset, MeasurementReading, LocalSiteWiseRegistry |
| | `classify_humidity_state()` — SiteWise Transform equivalent |
| | `compute_action_excursion_minutes()` — SiteWise Metric equivalent |
| | `apply_humidity_transform()` — classifies all stored readings |
| | `compute_excursion_duration()` — returns 22.0 for Dendrix scenario |

### Week 5 — Canonical model and state-of-control

| File | What it does |
|---|---|
| `src/aeros/kernel/models/canonical.py` | CanonicalEvent, AssuranceEvent, EventType, AssessmentOutcome, StateOfControlAssessment |
| `src/aeros/kernel/models/evidence.py` | EvidenceItem, EvidenceSourceType, EvidenceSource |
| `src/aeros/kernel/assurance/state_of_control.py` | `run_humidity_state_of_control()` + `build_assurance_events_from_assessment()` |
| `src/aeros/kernel/ingestion/event_router.py` | EventRouter + RoutingRule (IoT Rules Engine equivalent) |

### API

| File | What it does |
|---|---|
| `src/aeros/kernel/api/main.py` | `/health`, `/topology`, `/scenario/humidity-excursion`, `/state-of-control/humidity-excursion` |

### Tests

| File | Coverage |
|---|---|
| `tests/test_domain_models.py` | ISA-95, ISA-88, Sparkplug envelope |
| `tests/test_humidity_scenario.py` | 22-minute breach, supporting records |
| `tests/test_uns.py` | UNS topic builder, sanitization |
| `tests/test_local_sitewise.py` | Measurement storage, transform, excursion metric (11 tests) |
| `tests/test_state_of_control.py` | BREACH_CONFIRMED/ALERT/IN_CONTROL, lineage, EventRouter (18 tests) |

### Scripts

| File | What it does |
|---|---|
| `scripts/run_topology.sh` | Run plant topology simulation |
| `scripts/run_humidity_scenario.sh` | Run humidity excursion (with optional `--publish-mqtt`) |
| `scripts/run_mqtt_demo.sh` | Full MQTT demo: broker + subscriber + publish |
| `scripts/run_api.sh` | Start API server |

### Documentation

| File | What it covers |
|---|---|
| `docs/runbooks/00_local_development_quickstart.md` | macOS setup from scratch |
| `docs/runbooks/01_how_to_use_this_repo.md` | Repo layout + weekly learning path |
| `docs/runbooks/02_run_mqtt_simulation.md` | MQTT demo step-by-step |
| `docs/runbooks/03_run_opcua_to_mqtt_gateway.md` | OPC UA → MQTT gateway |
| `docs/runbooks/04_run_humidity_excursion_demo.md` | Demo scenarios + customer narrative |
| `docs/runbooks/05_run_api_server.md` | API server setup + endpoint reference |
| `docs/runbooks/06_test_and_debug.md` | Test commands + debugging guide |
| `docs/learning/00_concept_to_code_map.md` | Business concept → AWS → local MVP → code map |
| `docs/learning/week_01_domain_model.md` | ISA-95/88 learning + shop floor context |
| `docs/learning/week_02_uns_mqtt.md` | UNS, MQTT, Sparkplug B context |
| `docs/learning/week_03_opcua_greengrass_edge.md` | OPC UA, Greengrass, edge patterns |
| `docs/learning/week_04_sitewise_model.md` | SiteWise model: measurements, transforms, metrics |
| `docs/learning/week_05_state_of_control.md` | State-of-control, canonical events, event router |

---

## Known limitations

- No persistent storage: readings are in-memory; restart loses data.
- No authentication: MQTT broker is anonymous (local dev only).
- OPC UA concurrency is sequential: one tag read per poll cycle.
- Batch linkage is static: real implementation would query MES API.
- No human-approval workflow yet (Weeks 6–10).
- No graph relationships yet (Weeks 7–8).

---

## Next steps (Weeks 6–10)

| Week | What to build |
|---|---|
| 6 | Event-to-impact engine: link `StateOfControlAssessment` → batch → quality risk score |
| 7 | Evidence graph: Neptune-inspired graph with event→room→batch→product provenance nodes |
| 8 | GMP dossier builder: narrative generator from graph; Bedrock-assisted writing |
| 9 | APQR / deviation workflow: structured investigation templates, section generator |
| 10 | Control plane: persona APIs (QA, Engineering, Plant Head) + Bedrock Agents + MCP tools |
