# Areos AI Core Kernel (AWS-native foundation)

This repository is the initial **production-shaped MVP foundation** for Areos.ai core kernel.

Areos positioning used across this repo:

- **Areos.ai = Assurance, Reliability, Efficiency Operating System**
- **Do not sell monitoring; sell proof.**
- Existing systems monitor signals; Areos connects signals to validated state, product impact, and audit evidence.
- Utility event → area → batch/product/material → quality risk → evidence → decision.
- AI assists evidence generation; humans approve quality decisions.

## What is implemented in this first scaffold

- AWS-native architecture specs and learning curriculum (`specs/`, `docs/`)
- Tenant-aware Unified Namespace (UNS) topic builder
- Sparkplug-inspired event envelope model
- ISA-95 / ISA-88 foundational domain models
- OSD plant topology + humidity excursion scenario generator
- MQTT publish/subscribe local adapters
- OPC UA simulation scaffold with basic asyncua server
- Local SiteWise-like abstractions (`AssetModel`, `Measurement`, `Transform`, `Metric`)
- Local evidence object store scaffold and in-memory graph adapter
- FastAPI skeleton endpoints:
  - `GET /health`
  - `GET /topology`
  - `GET /scenario/humidity-excursion`

## Local vs AWS target mapping

| AWS target | Local MVP in this repo |
|---|---|
| AWS IoT Greengrass | Python edge gateway scaffold |
| AWS IoT Core MQTT | Local Mosquitto broker |
| AWS IoT SiteWise | Local SiteWise-like model abstraction |
| AWS IoT Rules Engine | Local ingestion/normalizer routing scaffold |
| Amazon S3 | `artifacts/evidence/...` local object store |
| Amazon Neptune | `NetworkXGraphAdapter` scaffold |
| Amazon Bedrock | Deferred; deterministic agent scaffolds later |

## Quick start

### 1) Install dependencies

```bash
python -m pip install -e .
```

### 2) Start local MQTT broker

```bash
docker compose up -d mosquitto
```

### 3) Run tests

```bash
pytest -q
```

### 4) Run API locally

```bash
uvicorn aeros.kernel.api.main:app --reload
```

## Safety and intended use

This MVP is **read-only-first** for OT/GxP safety. It is designed as a learning and architecture accelerator and is **intended to support validation workflows**. It does not claim regulator approval and does not perform autonomous quality decisions.

## Next steps

1. Add edge buffering/retry/dead-letter behavior and health telemetry.
2. Add state-of-control rule engine and event-to-impact logic.
3. Expand evidence graph relationship semantics and provenance.
4. Add Step Functions/EventBridge/Lambda target deployment stubs.
5. Add Bedrock/MCP tool-based agent orchestration for evidence drafting (human-approved).
