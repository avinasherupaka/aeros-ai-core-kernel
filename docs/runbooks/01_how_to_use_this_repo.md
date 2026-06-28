# 01 How to Use This Repository

> For the AWS-native Phase 1–2 path and week/day schedule, start with
> `docs/runbooks/00_start_here.md`.

## Purpose

This repository is designed to serve two simultaneous goals:

1. **Learning workspace** — each `docs/learning/` file maps a pharma/OT concept to its AWS architecture equivalent and then to the Python code implementing it locally.
2. **Working MVP** — the `src/` tree is runnable code, not pseudocode. Every learning concept has a corresponding implementation you can run and test.

---

## Repository layout

```
aeros-ai-core-kernel/
├── src/aeros/kernel/
│   ├── standards/          # ISA-95 hierarchy, ISA-88 batch model
│   ├── models/             # Canonical/assurance/evidence models
│   ├── simulation/         # OSD plant topology + humidity excursion demo
│   ├── ot/                 # UNS topic builder, MQTT publisher/subscriber,
│   │                       #   Sparkplug envelope, OPC UA sim + client
│   ├── ingestion/          # Edge gateway, normalizer, event router
│   ├── storage/            # Local SiteWise-like registry
│   ├── assurance/          # State-of-control engine
│   └── api/                # FastAPI application
├── tests/                  # pytest test suite
├── docs/
│   ├── architecture/       # AWS architecture diagrams and concepts
│   ├── glossaries/         # OT/IT, pharma GxP, AWS IoT glossaries
│   ├── learning/           # Week-by-week concept → code maps
│   └── runbooks/           # Step-by-step operational runbooks (you are here)
├── specs/                  # Product/architecture specifications
├── scripts/                # Shell helper scripts
└── docker/                 # Mosquitto MQTT broker config
```

---

## Weekly learning path

| Week | Topic | Learning doc | Key code |
|---|---|---|---|
| 1 | Domain model + plant topology | `docs/learning/week_01_domain_model.md` | `standards/`, `simulation/` |
| 2 | Unified Namespace + MQTT | `docs/learning/week_02_uns_mqtt.md` | `ot/uns.py`, `ot/mqtt_*.py` |
| 3 | OPC UA + edge gateway | `docs/learning/week_03_opcua_greengrass_edge.md` | `ot/opcua_*.py`, `ingestion/edge_gateway.py` |
| 4 | SiteWise-like asset model | `docs/learning/week_04_sitewise_model.md` | `storage/local_sitewise.py` |
| 5 | State-of-control engine | `docs/learning/week_05_state_of_control.md` | `assurance/state_of_control.py` |

---

## Areos design principles (use these in every conversation with pharma customers)

- **"Do not sell monitoring; sell proof."**
- **"Existing systems monitor signals; Areos connects signals to validated state, product impact, and audit evidence."**
- **"Utility event → area → batch/product/material → quality risk → evidence → decision."**
- **"Human-approved, audit-ready evidence packs."**
- **"Read-only-first for OT/GxP safety."**
- **"AI assists evidence generation; humans approve quality decisions."**

---

## How to navigate the code for a specific concept

1. Find the concept in `docs/learning/00_concept_to_code_map.md`.
2. The map points you to the relevant Python file and the spec that defines it.
3. Read the module-level docstring in that file — it explains the AWS equivalent.
4. Run the corresponding test to see it work.
5. Then read the learning doc for the deeper context.
