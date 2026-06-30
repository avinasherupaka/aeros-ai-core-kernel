# 00 Biopharma E2E Deterministic Test Guide

This guide is for **AWS dev-cell execution** of biopharma deterministic scenarios, including live-credential readiness with sample fallback.

## Section 1: Local sandbox prerequisites (Python, Docker, MQTT)

"Local sandbox" here means runtime-local on an AWS-hosted runner (not a personal machine).

```bash
cd /home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel
python -m pip install -e '.[dev]'
pytest -q tests/test_e2e_kernel_flow.py tests/test_phase6_live_connectors_and_backbone.py tests/test_event_api_connector_idempotency.py
```

Optional MQTT tooling in AWS-hosted shell:

```bash
docker compose up mqtt -d
```

## Section 2: Biologics bioreactor excursion demo (Scenario A)

Scenario key: `event::biotech_bioreactor_temperature_excursion`

### 2.1 Run bioreactor temperature simulation

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::biotech_bioreactor_temperature_excursion')
print(bundle.event.model_dump(mode='json'))
PY
```

### 2.2 Verify canonical event + fingerprint

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.algorithms.fingerprints import EventFingerprintInput, compute_event_fingerprint

bundle = get_demo_event_bundle('event::biotech_bioreactor_temperature_excursion')
e = bundle.event
fp = compute_event_fingerprint(EventFingerprintInput(
    tenant_id=e.tenant_id,
    site_id=e.site_id,
    source_system=e.source_system,
    source_record_id=e.event_id,
    source_timestamp=e.timestamp.isoformat(),
    parameter=e.metric,
    value=str(e.value),
    unit=e.unit or '',
    schema_version='1.0',
))
print({'event_id': e.event_id, 'fingerprint': fp})
PY
```

### 2.3 Verify state-of-control BREACH_CONFIRMED

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::biotech_bioreactor_temperature_excursion')
print({'outcome': bundle.assessment.outcome.value, 'excursion_minutes': bundle.assessment.excursion_duration_minutes})
assert bundle.assessment.outcome.value == 'BREACH_CONFIRMED'
PY
```

### 2.4 Verify cross-system evidence graph (BMS→Batch→QMS→EAM)

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.connectors import default_connector_registry, ConnectorReplayRequest
bundle = get_demo_event_bundle('event::biotech_bioreactor_temperature_excursion')
print({'nodes': len(bundle.evidence_graph.nodes), 'edges': len(bundle.evidence_graph.edges)})
for edge in bundle.evidence_graph.edges[:12]:
    print(edge.model_dump(mode='json'))

registry = default_connector_registry()
print(registry.replay('qms-veeva-vault-live', ConnectorReplayRequest(max_records=2)).get('records_out'))
print(registry.replay('cmms-infor-eam-live', ConnectorReplayRequest(max_records=2)).get('records_out'))
PY
```

Pass criteria:
- Graph contains lineage from sensor/system nodes to batch/product/risk/evidence nodes.
- Cross-system evidence is visible through connected node paths.

### 2.5 Generate GMP dossier + verify completeness score >= 0.85

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier

bundle = get_demo_event_bundle('event::biotech_bioreactor_temperature_excursion')
dossier = build_gmp_dossier(
    event=bundle.event,
    assessment=bundle.assessment,
    impact_assessment=bundle.impact,
    evidence_graph=bundle.evidence_graph,
    reliability_insight=bundle.reliability_insight,
)
print({'completeness_score': dossier.package_completeness_score, 'manifest': dossier.manifest_path})
assert dossier.package_completeness_score >= 0.85
PY
```

### 2.6 Ask QA agent: "Was BIO-BATCH-204 impacted?" -> verify answer

```bash
python - <<'PY'
from aeros.kernel.agents import AgentOrchestrator
agent = AgentOrchestrator()
answer = agent.ask('Was BIO-BATCH-204 impacted?')
print(answer)
PY
```

Pass criteria: response references impacted batch/risk/evidence logic and requires human QA review.

### 2.7 Verify idempotency: replay same event, confirm no new dossier

```bash
python - <<'PY'
from aeros.kernel.ingestion.event_api_connector import EventApiConnector
from aeros.kernel.ingestion.realtime_contracts import SourceSystemEvent, RealtimeSourceType

connector = EventApiConnector('acme_bio', 'bio_hyd_01')
event = SourceSystemEvent(
    event_id='bio-demo-dup-001',
    source_system='ignition',
    source_type=RealtimeSourceType.API_POLLING,
    tenant_id='acme_bio',
    site_id='bio_hyd_01',
    timestamp='2026-06-01T10:00:00+00:00',
    parameter='bioreactor_temperature',
    value='38.4',
    unit='degC',
)
ack1 = connector.ingest_event(event)
ack2 = connector.ingest_event(event)
print({'first_duplicate': ack1.is_duplicate, 'second_duplicate': ack2.is_duplicate})
assert ack2.is_duplicate is True
PY
```

## Section 3: Raw material quality variance demo (Scenario B)

### 3.1 Inject OOS LIMS result via EventApiConnector

```bash
python - <<'PY'
from aeros.kernel.ingestion.event_api_connector import EventApiConnector
from aeros.kernel.ingestion.realtime_contracts import SourceSystemEvent, RealtimeSourceType

connector = EventApiConnector('acme_bio', 'bio_hyd_01')
ack = connector.ingest_event(SourceSystemEvent(
    event_id='bio-lims-oos-001',
    source_system='labware',
    source_type=RealtimeSourceType.API_POLLING,
    tenant_id='acme_bio',
    site_id='bio_hyd_01',
    timestamp='2026-06-01T11:00:00+00:00',
    parameter='bioburden',
    value='120',
    unit='cfu_ml',
))
print(ack.model_dump(mode='json'))
PY
```

### 3.2 Verify ERP genealogy cross-reference

```bash
python - <<'PY'
from aeros.kernel.connectors import default_connector_registry, ConnectorReplayRequest
registry = default_connector_registry()
print(registry.replay('erp-sap-s4-odata-live', ConnectorReplayRequest(max_records=5)))
PY
```

### 3.3 Verify evidence graph: LabResult -> MaterialLot -> Batch -> Product

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::biotech_bioreactor_temperature_excursion')
for node in bundle.evidence_graph.nodes:
    if node.node_type.value in {'material_lot', 'batch', 'product', 'evidence'}:
        print(node.model_dump(mode='json'))
PY
```

### 3.4 Verify risk dashboard reflects variance

```bash
curl -s http://127.0.0.1:8000/workflows/plant-head-assurance | python3 -m json.tool
curl -s http://127.0.0.1:8000/workflows/validation-audit-room | python3 -m json.tool
```

## Section 4: AWS dev-cell post-deployment verification

### 4.1 IoT Thing certificate provisioning
- Follow `docs/runbooks/00_FULL_SYSTEM_TEST_AND_DEMO_GUIDE.md` Section 6.1.

### 4.2 MQTT publish to IoT Core -> CloudWatch Logs confirmation

```bash
IOT_ENDPOINT="$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)"
TOPIC="areos/acme-pharma/hyd-site-01/utility/bioreactor_suite/bioreactor_201/temperature"
aws iot-data publish --endpoint-url "https://$IOT_ENDPOINT" --topic "$TOPIC" --qos 1 --payload '{"value":38.4,"unit":"degC"}'
aws logs tail /areos/dev/iot --since 5m
```

### 4.3 S3 bronze partition creation

```bash
aws s3 ls "s3://$(cd infra/terraform/envs/dev && terraform output -raw evidence_bucket_name)/bronze/" --recursive | head
```

### 4.4 DynamoDB idempotency record confirmation

```bash
TABLE="$(cd infra/terraform/envs/dev && terraform output -raw event_metadata_table_name)"
aws dynamodb scan --table-name "$TABLE" --max-items 20
```

## Section 5: Deterministic output verification (hash comparison)

```bash
API_BASE_URL="http://127.0.0.1:8000"
PAYLOAD='{"source_system":"ignition","parameter":"bioreactor_temperature","value":"38.4","unit":"degC","event_id":"bio-det-001","timestamp":"2026-06-01T10:00:00+00:00"}'

R1="$(curl -s -X POST "$API_BASE_URL/ingestion/events/simulate" -H 'content-type: application/json' -d "$PAYLOAD")"
R2="$(curl -s -X POST "$API_BASE_URL/ingestion/events/simulate" -H 'content-type: application/json' -d "$PAYLOAD")"

H1="$(echo "$R1" | jq -cS . | sha256sum | awk '{print $1}')"
H2="$(echo "$R2" | jq -cS . | sha256sum | awk '{print $1}')"

printf "run1=%s\nrun2=%s\n" "$H1" "$H2"
```

Pass criteria: `run1 == run2` and second response `is_duplicate=true`.

## Section 6: Tenant isolation verification

```bash
python - <<'PY'
from aeros.kernel.algorithms.fingerprints import EventFingerprintInput, compute_event_fingerprint
base = dict(site_id='bio_hyd_01', source_system='ignition', source_record_id='evt-01', source_timestamp='2026-06-01T10:00:00+00:00', parameter='bioreactor_temperature', value='38.4', unit='degC', schema_version='1.0')
fp_a = compute_event_fingerprint(EventFingerprintInput(tenant_id='tenant_a', **base))
fp_b = compute_event_fingerprint(EventFingerprintInput(tenant_id='tenant_b', **base))
print({'tenant_a': fp_a, 'tenant_b': fp_b, 'different': fp_a != fp_b})
assert fp_a != fp_b
PY
```

## Section 7: CSV/IQ/OQ evidence capture

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="artifacts/validation/biopharma/$STAMP"
mkdir -p "$ROOT"/{iq,oq,pq,hashes,aws,api}

curl -s http://127.0.0.1:8000/connectors/health > "$ROOT/api/connectors_health.json"
curl -s http://127.0.0.1:8000/enterprise/readiness > "$ROOT/api/enterprise_readiness.json"
```

Capture matrix:
- IQ: Terraform outputs, IoT/Greengrass/SiteWise existence proof.
- OQ: deterministic replay hash report, duplicate replay proof, connector validation outputs.
- PQ: Scenario A + B outputs, dossier manifests/hashes, workflow screen/API evidence.

---

## Biologics demo script (AWS-hosted execution)

`run_humidity_scenario.sh` and `run_mqtt_demo.sh` are OSD-centric. Use this biologics sequence:

```bash
uvicorn aeros.kernel.api.main:app --host 0.0.0.0 --port 8000

curl -s http://127.0.0.1:8000/assurance/events/event::biotech_bioreactor_temperature_excursion/state-of-control | python3 -m json.tool
curl -s http://127.0.0.1:8000/assurance/events/event::biotech_bioreactor_temperature_excursion/impact | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8000/dossiers/events/event::biotech_bioreactor_temperature_excursion/generate-package | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8000/answers/qa-impact/biotech_bioreactor_temperature_excursion | python3 -m json.tool
```

---

## E2E suite structure reusable across industries (OSD, Biopharma, others)

```
E2E_SUITE/
  01_preconditions/
  02_ingestion_and_connector_resolution/
  03_assurance_state_and_impact/
  04_evidence_graph_and_dossier/
  05_determinism_and_idempotency/
  06_fault_injection/
  07_csv_iq_oq_pq_export/
```

Use biopharma as the template pack; replicate with OSD scenario IDs for parity.
