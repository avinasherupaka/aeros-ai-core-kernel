# 000 Master Build Curriculum (AWS-native)

## Weeks 1–5 — **Implemented in this PR**

| Week | Topic | Status | Key files |
|---|---|---|---|
| 1 | ISA-95/88 domain model + OSD plant topology | ✅ Implemented | `standards/`, `simulation/plant_topology.py` |
| 2 | Unified Namespace + MQTT backbone | ✅ Implemented | `ot/uns.py`, `ot/mqtt_*.py`, `ot/sparkplug_envelope.py` |
| 3 | OPC UA simulation + Greengrass-style edge gateway | ✅ Implemented | `ot/opcua_*.py`, `ingestion/edge_gateway.py` |
| 4 | SiteWise-like asset model and time-series ingestion | ✅ Implemented | `storage/local_sitewise.py` |
| 5 | Canonical model, state-of-control engine, event router | ✅ Implemented | `assurance/state_of_control.py`, `ingestion/event_router.py`, `models/canonical.py` |

See `specs/007_weeks_1_to_5_implementation_map.md` for navigation guide.

---

## Weeks 6–10 — Next path

| Week | Topic | Notes |
|---|---|---|
| 6 | Event-to-impact engine | Link breach → batch/product → quality risk assessment |
| 7 | Evidence graph + provenance | Neptune-like graph: event→room→batch→evidence node |
| 8 | GMP dossier builder | Human-readable evidence packs from the graph; Bedrock-assisted narrative |
| 9 | APQR/deviation workflow | Structured deviation investigation support; APQR section generator |
| 10 | Control plane + persona views + Agents/MCP | QA, Engineering, Plant Head views; Bedrock Agents; MCP tool integration |

---

## Full topic list (original)

1. AWS-native OT/IT assurance architecture + Areos manifesto language.
2. ISA-95 + ISA-88 domain model implementation.
3. Unified Namespace + MQTT + Sparkplug-inspired payload patterns.
4. Greengrass-style edge gateway and OPC UA simulation.
5. SiteWise-like asset model and time-series ingestion.
6. Event routing, canonical normalization, and data quality gates.
7. State-of-control engine.
8. Event-to-impact engine.
9. Evidence graph + GMP dossier builder.
10. Control plane/persona modules.
11. Agents/Bedrock/MCP integration.
