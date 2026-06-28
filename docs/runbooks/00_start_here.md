# 00 Start Here

## What this repository is now

- **Product runtime target:** AWS-native tenant-site cells.
- **Local code purpose:** developer sandbox, simulation harness, and unit/integration test accelerator.
- **Positioning:** Areos is a **system of assurance, not a system of record**.

## Week/day learning + build schedule (Phase 1–2)

### Week 1 (Cloud-native foundation)
- Day 1: Read `specs/008_enterprise_32_week_roadmap.md` and `docs/architecture/cloud_native_foundation.md`.
- Day 2: Configure AWS CLI/SSO and Terraform (`02_aws_account_prerequisites.md`).
- Day 3: Run `terraform plan` in `infra/terraform/envs/dev`.
- Day 4: Review security/compliance mapping docs.
- Day 5: Validate CI pipeline and document evidence.

### Week 2 (Tenant-site cell)
- Day 1–2: Configure tenant/site IDs and isolation strategy.
- Day 3: Plan/apply tenant-site metadata resources in dev.
- Day 4: Review data residency and IAM boundaries.
- Day 5: Capture validation evidence.

### Week 3 (Zero trust baseline)
- Day 1: Read threat model docs.
- Day 2: Validate read-only OT connector assumptions.
- Day 3: Review cert identity model for IoT devices.
- Day 4: Review ransomware resilience controls.
- Day 5: Update risk register and controls checklist.

### Week 4 (CI/CD lifecycle)
- Day 1: Review GitHub OIDC role wiring.
- Day 2: Enable `terraform-plan` workflow.
- Day 3: Run manual `deploy-dev` workflow.
- Day 4: Store deployment validation artifacts.
- Day 5: Teardown/redeploy dry run.

### Week 5 (IoT Core + UNS)
- Day 1: Read `docs/architecture/unified_namespace_design.md`.
- Day 2: Plan IoT module changes.
- Day 3: Provision policy/thing/rule scaffold.
- Day 4: Publish tenant/site-scoped MQTT test payloads.
- Day 5: Validate CloudWatch routing.

### Week 6 (Greengrass V2)
- Day 1–2: Review component recipes.
- Day 3: Map local collector to Greengrass V2 component/deployment model.
- Day 4: Validate read-only connector mode.
- Day 5: Document deployment versioning.

### Week 7 (Connector foundation)
- Day 1: Read `specs/009_connector_sdk_and_industry_pack_strategy.md`.
- Day 2: Implement/verify connector manifests.
- Day 3: Validate file import connector tests.
- Day 4: Map MQTT/OPC UA connector lineage fields.
- Day 5: Define next connector pack priorities.

### Week 8 (SiteWise modeling)
- Day 1: Review model strategy + JSON template.
- Day 2: Plan SiteWise module with resources disabled.
- Day 3: Enable in sandbox if approved.
- Day 4: Validate model properties and hierarchy.
- Day 5: Capture model evidence artifacts.

## Concept-to-code playbook

1. Read the matching spec/architecture doc first.
2. Locate implementation path under `src/aeros/kernel/` or `infra/terraform/`.
3. Run focused tests (`pytest tests/<file>.py -v`).
4. Run integration checks from runbooks.
5. Record evidence for release validation.

Continue with `01_local_developer_sandbox.md` for local flow or `02_aws_account_prerequisites.md` for AWS setup.
