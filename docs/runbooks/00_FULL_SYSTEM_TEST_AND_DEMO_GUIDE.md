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

## 11) Known limits (as of current repo state)

- Some live connector behaviors remain scaffolded and require customer-specific runtime integration.
- Greengrass provisioning/deployment orchestration is architecture-aligned, not fully automated in Terraform.
- SiteWise resources are optional by default (`enable_sitewise_resources=false`).
- Customer CSV governance, approvals, and release controls remain deployment-program work.
