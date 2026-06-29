# 00 Full System Test and Demo Guide

This is the single end-to-end setup, test, and demo guide for the current repository state.

## 1. What this repo contains and does not yet contain

Contains:
- Local deterministic sandbox for ontology, assurance engines, dossiers, workflows, connectors, and persona agents.
- AWS-native Terraform and Greengrass V2 architecture scaffolding.
- Local sample datasets for Phase 6 connector testing.

Does not yet contain:
- Live production integrations to enterprise source systems.
- Required Bedrock credentials/runtime for hosted agent execution.
- A claim of automatic 21 CFR Part 11 compliance.

## 2. Architecture overview

- Local sandbox/test harness: `src/aeros/kernel/*`, `artifacts/*`, `tests/*`
- AWS-native tenant-site cell runtime: `infra/terraform/*`
- Greengrass V2 edge architecture: `edge/greengrass/*`, `docs/architecture/greengrass_v2_edge_gateway.md`
- Connector ecosystem: `src/aeros/kernel/connectors/*`
- Assurance engines: `src/aeros/kernel/assurance/*`
- Evidence package and control plane: `src/aeros/kernel/dossiers/*`, `src/aeros/kernel/workflows/*`, `src/aeros/kernel/api/main.py`
- Deterministic agents: `src/aeros/kernel/agents/*`

## 3. Prerequisites

- macOS or Linux shell tools
- Python 3.11+
- Terraform
- AWS CLI
- AWS account/profile for dev-cell validation only
- GitHub OIDC understanding for CI/CD docs review

## 4. Local setup

```bash
cd /home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
pytest -q
```

## 5. Local sandbox tests

```bash
bash scripts/run_topology.sh
bash scripts/run_humidity_scenario.sh
bash scripts/run_mqtt_demo.sh   # if MQTT demo tooling is desired locally
pytest -q tests/test_humidity_scenario.py tests/test_uns.py
```

## 6. Phase 1-2 AWS dev-cell plan/deploy testing

Plan-first only:

```bash
bash scripts/terraform_validate.sh
cd infra/terraform
terraform init
terraform validate
terraform plan -out dev.tfplan
```

Guidance:
- Review plans before any apply.
- Use isolated dev accounts/profiles.
- Tear down unused resources promptly.
- Follow `docs/runbooks/08_teardown_and_cost_control.md` for spend control.

## 7. Phase 3-5 product kernel tests

```bash
python - <<'PY'
from aeros.kernel.ontology.industry_packs import list_industry_packs
from aeros.kernel.api.demo_data import list_demo_events, get_demo_event_bundle
print(list_industry_packs())
print(list_demo_events()[:3])
bundle = get_demo_event_bundle('event::pharma_osd_humidity_excursion_compression')
print(bundle.assessment.model_dump(mode='json'))
print(bundle.impact.model_dump(mode='json'))
print(bundle.evidence_graph.model_dump(mode='json'))
print(bundle.dossier.model_dump(mode='json')['package_completeness_score'])
PY
```

APQR/PQR section:

```bash
python - <<'PY'
from aeros.kernel.agents.tools import AgentToolRegistry
print(AgentToolRegistry().generate_apqr_section('enterprise_demo'))
PY
```

Inspect workflow views:

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import workflow_views
print(workflow_views()['deviation_queue'].model_dump(mode='json'))
print(workflow_views()['engineering_reliability_board'].model_dump(mode='json'))
print(workflow_views()['plant_head_assurance'].model_dump(mode='json'))
print(workflow_views()['validation_audit_room'].model_dump(mode='json'))
PY
```

## 8. Phase 6 connector tests

```bash
pytest -q \
  tests/test_connector_sdk_hardened.py \
  tests/test_historian_connector_pack.py \
  tests/test_qms_mes_connector_pack.py \
  tests/test_cmms_erp_lims_connector_pack.py \
  tests/test_connector_validation_pack.py
```

Manual examples:

```bash
python - <<'PY'
from datetime import datetime, timezone
from aeros.kernel.connectors import ConnectorReplayRequest, default_connector_registry
registry = default_connector_registry()
print(registry.list_connectors())
print(registry.validate('historian-aveva-pi'))
print(registry.replay('historian-aveva-pi', ConnectorReplayRequest(
    start_time=datetime(2026,6,1,10,5,tzinfo=timezone.utc),
    end_time=datetime(2026,6,1,10,15,tzinfo=timezone.utc),
)))
print(registry.generate_validation_pack('historian-aveva-pi', 'artifacts/connectors/validation'))
PY
```

## 9. Phase 7 agent tests

```bash
pytest -q \
  tests/test_agent_tools.py \
  tests/test_qa_agent.py \
  tests/test_engineering_agent.py \
  tests/test_plant_head_agent.py \
  tests/test_validation_agent.py \
  tests/test_agent_orchestrator.py
```

Manual examples:

```bash
python - <<'PY'
from aeros.kernel.agents import AgentOrchestrator
agent = AgentOrchestrator()
print(agent.ask('Was Batch BATCH-OSD-2026-001 potentially impacted?'))
print(agent.ask('Which assets are recurring hotspots?'))
print(agent.ask('What happened and what should I care about?'))
print(agent.ask('Is the evidence package audit-ready?'))
PY
```

## 10. API test sequence

Start API:

```bash
uvicorn aeros.kernel.api.main:app --reload
```

Then call key endpoints:

```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
curl -s http://127.0.0.1:8000/assurance/demo-events | python3 -m json.tool
curl -s http://127.0.0.1:8000/connectors/registry | python3 -m json.tool
curl -s http://127.0.0.1:8000/connectors/health | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8000/connectors/historian-aveva-pi/validate | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8000/connectors/historian-aveva-pi/replay -H 'content-type: application/json' -d '{"start_time":"2026-06-01T10:05:00+00:00","end_time":"2026-06-01T10:15:00+00:00"}' | python3 -m json.tool
curl -s http://127.0.0.1:8000/connectors/historian-aveva-pi/validation-pack | python3 -m json.tool
curl -s http://127.0.0.1:8000/agents/tools | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8000/agents/ask -H 'content-type: application/json' -d '{"question":"Was Batch BATCH-OSD-2026-001 potentially impacted?"}' | python3 -m json.tool
curl -s http://127.0.0.1:8000/enterprise/readiness | python3 -m json.tool
```

## 11. Functional demo script

### 15-minute founder demo

1. Start with positioning: do not sell monitoring; sell proof.
2. Show a demo event and connect it to state-of-control.
3. Show batch/product impact and missing evidence.
4. Show generated dossier and workflow views.
5. Show connector registry and replay on a historian sample.
6. Ask QA and plant-head questions via `/agents/ask`.

### 45-minute technical walkthrough

- Walk Phase 1-2 architecture and Terraform plan-first path.
- Walk Phase 3-5 event -> impact -> evidence -> dossier chain.
- Walk Phase 6 manifests, contracts, mapping rules, replay, validation pack.
- Walk Phase 7 deterministic tool registry, orchestrator, and future Bedrock/MCP seam.

### Persona messaging

- QA: human-approved, audit-ready evidence packs.
- Engineering: recurrence hotspots and post-maintenance recurrence visibility.
- IT/OT: read-only-first connectors, tenant/site scoping, AWS-native target runtime.
- Validation: supports Part 11/GxP controls, auditability, and CSV; does not auto-claim compliance.

## 12. Troubleshooting

- Import errors: ensure editable install is active and `pytest -q` works locally.
- Test failures: run the targeted test files above before full suite re-run.
- Terraform issues: validate provider auth/profile and run `terraform validate` before `plan`.
- AWS credentials: not required for local Phase 3-7 testing.
- Generated artifacts: local connector validation packs live under `artifacts/connectors/validation/`; dossier artifacts under ignored `artifacts/evidence/`.

## 13. Known limitations and next productization steps

- Live enterprise connectors remain future work.
- Bedrock/MCP runtime is scaffolded, not required for local testing.
- Enterprise resilience/load testing is documented, not fully automated.
- Customer-specific validation, IQ/OQ/PQ, and production release controls remain implementation/deployment work.
