# 00 Full System Test and Demo Guide (AWS Dev Environment First)

This is the master end-to-end guide for running Areos in an **AWS dev environment** for client-style demo/test execution.

> Operator stance: run all commands from AWS-hosted execution (CloudShell, EC2 via SSM, CodeBuild runner, or GitHub Actions runner). Do not depend on a user laptop.

## 1) Current state summary

Included now:
- Deterministic assurance kernel, dossier/workflow engines, API, and test harness.
- Terraform scaffolding for tenant-site dev cell (`infra/terraform/envs/dev`).
- Connector packs with sample datasets plus live connector metadata.
- Deterministic algorithms for fingerprinting/idempotency and answer generation.

Not yet fully productized:
- Full live enterprise connector credential orchestration and customer-specific mappings.
- Complete managed production deployment stack for all runtime services.
- Automatic 21 CFR Part 11 compliance claims (customer CSV still required).

## 2) AWS-only execution baseline

Run from an AWS-hosted shell with:
- Python 3.11+
- Terraform >= 1.6
- AWS CLI v2
- Access to target dev account/role

Repository path (example runner):

```bash
cd /home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel
python -m pip install -e '.[dev]'
pytest -q
```

## 3) Live system prerequisites + fallback model

### 3.1 Required target integrations for live simulation

Prepare these interfaces for customer/live mode:
- Veeva Vault (OAuth2) — QMS deviations
- SAP S/4HANA OData — genealogy/material context
- Ignition Historian REST — bioreactor/process telemetry
- Rockwell PharmaSuite REST/API — MES batch timeline
- Infor EAM REST — maintenance/work-order evidence

### 3.2 Fallback behavior contract (dev-safe)

Final expected behavior for demos/tests:
- If live credentials/endpoints are **present**: use live interfaces.
- If missing/blank: use connector sample datasets under `artifacts/connectors/sample_data/*`.
- This keeps the same end-to-end flow, so customer credential onboarding is a configuration/mapping step, not a flow rewrite.

## 4) Connector credential injection procedure (no secrets in repo)

### 4.1 Secret sources (preferred order)
1. AWS Secrets Manager / SSM Parameter Store
2. Runtime environment variables injected by deploy platform
3. Secure file upload fallback (certificate/key bundles), mounted at runtime

### 4.2 Required secret payloads (minimum)
- `VEEVA_VAULT_CLIENT_ID`, `VEEVA_VAULT_CLIENT_SECRET`, `VEEVA_VAULT_TOKEN_URL`, `VEEVA_VAULT_BASE_URL`
- `SAP_ODATA_CLIENT_ID`, `SAP_ODATA_CLIENT_SECRET`, `SAP_ODATA_BASE_URL`
- `IGNITION_API_KEY`, `IGNITION_BASE_URL`
- `PHARMASUITE_API_KEY`, `PHARMASUITE_BASE_URL`
- `INFOR_EAM_API_KEY`, `INFOR_EAM_BASE_URL`

### 4.3 Injection example (AWS CLI + env export)

```bash
export VEEVA_VAULT_CLIENT_ID="$(aws secretsmanager get-secret-value --secret-id areos/dev/veeva --query 'SecretString' --output text | jq -r '.client_id')"
export VEEVA_VAULT_CLIENT_SECRET="$(aws secretsmanager get-secret-value --secret-id areos/dev/veeva --query 'SecretString' --output text | jq -r '.client_secret')"
export SAP_ODATA_BASE_URL="$(aws ssm get-parameter --name /areos/dev/sap/base_url --with-decryption --query 'Parameter.Value' --output text)"
```

### 4.4 File upload fallback (cert/key)
- Upload cert/key to a secure runtime path (example: `/opt/areos/connector-secrets/`).
- Inject only the file paths as env vars (never inline secret contents in config files).
- Keep files out of git and out of Terraform state.

## 5) AWS dev-cell deploy and runtime wiring

```bash
cd /home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel/infra/terraform/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
terraform plan -out tfplan
terraform apply tfplan
terraform output
```

Capture these outputs:
- `iot_thing_name`
- `event_metadata_table_name`
- `evidence_bucket_name`

Optional runtime env (only when using a DynamoDB table that matches the connector idempotency schema):

```bash
export AREOS_BRONZE_BUCKET="$(terraform output -raw evidence_bucket_name)"
export AWS_REGION="ap-south-1"
```

## 6) AWS post-deploy verification sequence

### 6.1 IoT Thing certificate provisioning (outside Terraform)

```bash
IOT_THING_NAME="$(terraform output -raw iot_thing_name)"
IOT_POLICY_NAME="areos-acme-pharma-hyd-site-01-policy"   # replace for your tenant/site

aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile /tmp/areos-device-cert.pem \
  --public-key-outfile /tmp/areos-device-public.key \
  --private-key-outfile /tmp/areos-device-private.key > /tmp/iot-cert.json

CERT_ARN="$(jq -r '.certificateArn' /tmp/iot-cert.json)"
aws iot attach-thing-principal --thing-name "$IOT_THING_NAME" --principal "$CERT_ARN"
aws iot attach-policy --policy-name "$IOT_POLICY_NAME" --target "$CERT_ARN"
```

### 6.2 Greengrass core device registration check

```bash
aws greengrassv2 list-core-devices
aws greengrassv2 get-core-device --core-device-thing-name "$IOT_THING_NAME"
```

### 6.3 SiteWise asset ingestion check

```bash
aws iotsitewise list-asset-models --max-results 20
# If SiteWise resources are disabled, use artifacts/sitewise/osd_sitewise_models.example.json as the expected model contract.
```

### 6.4 DynamoDB event write confirmation

Confirm dev-cell DynamoDB write/read using the provisioned tenant-site table schema (`pk` / `sk`):

```bash
TABLE_NAME="$(terraform output -raw event_metadata_table_name)"
PK="tenant#acme-pharma#site#hyd-site-01"
SK="event#$(date -u +%Y%m%dT%H%M%SZ)"

aws dynamodb put-item \
  --table-name "$TABLE_NAME" \
  --item "{\"pk\":{\"S\":\"$PK\"},\"sk\":{\"S\":\"$SK\"},\"event_type\":{\"S\":\"post_deploy_smoke\"},\"status\":{\"S\":\"ok\"}}"

aws dynamodb get-item \
  --table-name "$TABLE_NAME" \
  --key "{\"pk\":{\"S\":\"$PK\"},\"sk\":{\"S\":\"$SK\"}}"
```

## 7) Deterministic replay verification (same input -> same output hash)

```bash
API_BASE_URL="http://127.0.0.1:8000"
PAYLOAD='{"source_system":"ignition","parameter":"bioreactor_temperature","value":"38.4","unit":"degC","event_id":"deterministic-evt-001","timestamp":"2026-06-01T10:00:00+00:00"}'

RESP1="$(curl -s -X POST "$API_BASE_URL/ingestion/events/simulate" -H 'content-type: application/json' -d "$PAYLOAD")"
RESP2="$(curl -s -X POST "$API_BASE_URL/ingestion/events/simulate" -H 'content-type: application/json' -d "$PAYLOAD")"

HASH1="$(echo "$RESP1" | jq -cS . | sha256sum | awk '{print $1}')"
HASH2="$(echo "$RESP2" | jq -cS . | sha256sum | awk '{print $1}')"

echo "hash1=$HASH1"
echo "hash2=$HASH2"
# Pass criteria: HASH1 == HASH2
# Also expect second call to return is_duplicate=true.
```

## 8) Fault injection test procedure

### 8.1 Disconnect historian mid-ingestion
- Remove/blank historian live endpoint variables.
- Re-run connector health/replay and verify sample fallback still produces normalized records.

### 8.2 Replay duplicate events
- POST same simulated event twice.
- Verify second response `is_duplicate=true` and no additional non-duplicate evidence artifact.

### 8.3 Inject out-of-order timestamps
- POST event B (later timestamp) then event A (earlier timestamp).
- Verify both are accepted, each has deterministic fingerprint, and ordering is traceable in lineage timestamps.

## 9) CSV / IQ / OQ / PQ evidence capture

Create a validation evidence package per run:

```bash
EVIDENCE_ROOT="artifacts/validation/aws-dev/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$EVIDENCE_ROOT"/{iq,oq,pq,logs,hashes,screenshots}
```

Minimum required captures:
- **IQ**: Terraform plan/apply output, resource IDs, IoT/Greengrass/SiteWise/DynamoDB existence checks.
- **OQ**: Deterministic replay proof, duplicate handling proof, connector health/validation outputs.
- **PQ**: Scenario execution outputs (OSD + biopharma), QA-agent response checks, dossier completeness checks.

Store at least:
- `/connectors/health`, `/connectors/registry`, `/enterprise/readiness` responses
- deterministic hash comparison file
- dossier manifest/package hashes
- AWS CLI command output logs

## 10) E2E test suite structure (OSD + biopharma)

One-command automation (local/AWS-hosted runner sandbox):

```bash
cd /home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel
./scripts/run_magic_e2e_suite.sh
```

This single invocation runs validation tests plus deterministic orchestration and writes a timestamped evidence package to `artifacts/validation/e2e_magic/`.

### 10.1 What validation/evidence this command provides

`./scripts/run_magic_e2e_suite.sh` does two things, in order:

1. Runs the E2E validation pytest pack (kernel flow, connectors, idempotency, state-of-control, impact, evidence graph, dossier packaging, workflow views, deterministic answers, and magic suite tests).
2. Runs deterministic demo orchestration (`python -m aeros.kernel.simulation.e2e_magic_suite`) that exports a timestamped evidence package under `artifacts/validation/e2e_magic/`.

Evidence produced by this flow includes:
- Pass/fail evidence from pytest for each required E2E behavior area.
- Dossier package artifacts (`dossier.md`, `dossier.json`, `manifest.json`, `evidence_index.json`, `source_citations.json`, `missing_evidence_checklist.json`, `approval_placeholder.json`, `package_hashes.json`).
- Deterministic replay outputs and generated run artifacts captured by the orchestration step.

### 10.2 How to read results and confirm E2E is working

Treat E2E as healthy when all of the following are true:

1. The pytest run ends with no failures (all targeted suite tests pass).
2. A new timestamped folder appears in `artifacts/validation/e2e_magic/` for the current run.
3. The run folder contains expected dossier/evidence artifacts and non-empty JSON/markdown outputs.
4. `package_hashes.json` contains SHA-256 entries for package files, showing integrity metadata was generated.
5. `manifest.json` and `source_citations.json` contain the expected event/package metadata and traceable source citation fields.

Quick verification commands:

```bash
# 1) Confirm latest E2E evidence directory was created
ls -1dt artifacts/validation/e2e_magic/* | head -1

# 2) Inspect generated artifact set in the latest run
LATEST_RUN="$(ls -1dt artifacts/validation/e2e_magic/* | head -1)"
find "$LATEST_RUN" -maxdepth 4 -type f | sort

# 3) Spot-check package integrity and citation presence
find "$LATEST_RUN" -name package_hashes.json -o -name source_citations.json -o -name manifest.json
```

Use one framework and two scenario packs:
- OSD pack (humidity/pressure/dew-point)
- Biopharma pack (bioreactor temp/pH, WFI, cold-room)

Reusable suite phases:
1. Preconditions (credentials/endpoint/fallback resolution)
2. Ingestion and normalization
3. State-of-control and impact
4. Evidence graph and dossier
5. Determinism/idempotency
6. Fault handling
7. CSV evidence export

For the full biopharma deterministic walkthrough, use:
- `docs/runbooks/00_BIOPHARMA_E2E_DETERMINISTIC_TEST_GUIDE.md`

## 11) Control Plane UI (read-only SCADA-lite view)

The Control Plane UI translates verbose validation evidence into a human-readable workflow for QA, operations, engineering, and leadership. It is intentionally **read-only** in this phase: it visualizes status, evidence, and workflow readiness, but does not write back to OT systems or approve GxP decisions.

Start the local API/UI after running the E2E suite:

```bash
./scripts/run_magic_e2e_suite.sh
uvicorn aeros.kernel.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/control-plane
```

The backing API endpoints are:

```text
GET  /control-plane/api/overview
GET  /control-plane/api/topology
GET  /control-plane/api/readiness
GET  /control-plane/api/data-flows
GET  /control-plane/api/personas/system_admin
GET  /control-plane/api/personas/qa
GET  /control-plane/api/personas/plant_ops
POST /control-plane/api/assistant/query
```

### 11.1 What the UI normalizes

The UI/API reads the latest timestamped folder under `artifacts/validation/e2e_magic/` and normalizes:

- `summary.json` into run status and top-level validation checks.
- `preconditions.json` into connector/edge readiness.
- `ingestion.json` into connector validation, replay, and idempotency status.
- `assurance.json` into state-of-control and impact readiness.
- `dossier.json` into package/evidence readiness.
- `workflows_answers.json` into QA, Ops, Engineering, and Leadership views.

The frontend does not parse these raw files directly. It calls the normalized control-plane API, which is the same shape an MCP server should use for grounded answers.

### 11.2 How to read the traffic-light status

Traffic-light indicators mean:

- **Green**: validation or workflow stage is complete and no immediate evidence/action gap is detected.
- **Yellow**: pipeline is functioning, but there is an active excursion, missing evidence, pending human approval, or audit-readiness closure item.
- **Red**: critical severity or failed connector/readiness condition requires immediate triage.

Readiness is shown at multiple levels:

- **Workflow stage**: preconditions, ingestion, assurance, dossier, persona workflows.
- **Site/area/asset**: SCADA-lite map rendered as human-readable manufacturing domain paths.
- **Data flows**: directional integration telemetry across BMS/LIMS/ERP/QMS/CMMS to the control-plane backbone.
- **Persona**: role-specific workflows for System Administrator, QA, and Plant Ops.

### 11.3 AWS alignment

The local UI is designed to map cleanly to the target AWS architecture:

- **AWS IoT Greengrass**: edge core/component/device health and connector last-seen status.
- **AWS IoT Core**: MQTT ingestion, event routing, and source event envelopes.
- **AWS IoT SiteWise**: site/area/asset hierarchy, asset models, property values, alarms, and quality flags.
- **S3 evidence lake**: dossier packages, source citations, package hashes, and validation evidence.
- **DynamoDB/Aurora**: workflow state, acknowledgements, CAPA/deviation queue state in later phases.
- **MCP/assistant layer**: queries normalized control-plane APIs and evidence graph relationships, not raw JSON files.

### 11.4 Embedded assistant usage

Use the assistant panel or API to ask grounded questions:

```bash
curl -s http://127.0.0.1:8000/control-plane/api/assistant/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Why is the system yellow?","persona":"qa"}' | python -m json.tool
```

Expected answer shape:

- `summary`: human-readable explanation.
- `response_markdown`: guided, step-by-step markdown response.
- `grounding_sources`: evidence locations and normalized model references.
- `human_approval_required`: always true for GxP-impacting decisions.

### 11.5 Phase boundaries

Current scope:

- Read-only visualization.
- Latest-run evidence normalization.
- SCADA-lite topology and R/Y/G readiness.
- Persona dashboards.
- Grounded assistant contract.

Not in current scope:

- Alarm acknowledgement writes.
- CAPA creation/update writes.
- Greengrass command/control.
- Automated remediation.
- Human approval replacement.

Those belong to later workflow-action and closed-loop orchestration phases.

## 12) Known limits (as of current repo state)

- Some live connector behaviors remain scaffolded and require customer-specific runtime integration.
- Greengrass provisioning/deployment orchestration is architecture-aligned, not fully automated in Terraform.
- SiteWise resources are optional by default (`enable_sitewise_resources=false`).
- Customer CSV governance, approvals, and release controls remain deployment-program work.
