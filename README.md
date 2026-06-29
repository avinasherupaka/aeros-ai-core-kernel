# Areos AI Core Kernel (AWS-native enterprise foundation)


## Architecture and runbook entry points

- `docs/architecture/mission_critical_target_architecture.md`
- `docs/architecture/master_architecture_diagram.md`
- `docs/runbooks/00_FULL_SYSTEM_TEST_AND_DEMO_GUIDE.md`

Areos.ai = **Assurance, Reliability, Efficiency Operating System**.

- Areos is a **system of assurance, not a system of record**.
- **Do not sell monitoring; sell proof.**
- Existing systems monitor signals and store records; Areos connects signals to validated state, product impact, and audit evidence.
- Utility event → area → batch/product/material → quality risk → evidence → decision.
- Human-approved, audit-ready evidence packs.
- Read-only-first for OT/GxP safety.
- AI assists evidence generation; humans approve quality decisions.

## Repository positioning

- **Target runtime (product):** AWS-native tenant-site cell.
- **Local runtime:** developer sandbox, simulator, and test harness.

## What is included

### Phase 1 foundation
- Terraform scaffolding for foundation, evidence lake, observability, tenant-site cell, GitHub OIDC.
- Zero-trust/security/compliance/runbook documentation.
- CI/CD workflows for Python + Terraform and OIDC-based deploy scaffolding.

### Phase 2 backbone
- Terraform scaffolding for IoT Core and SiteWise model seed.
- Greengrass V2 component recipe skeletons.
- Connector SDK foundation (`src/aeros/kernel/connectors`) + tests.

### Phase 3–5 product batch
- Universal regulated-operations ontology + industry packs.
- Assurance engines for canonical events, state-of-control, event-to-impact, recurrence, and evidence graph.
- GMP dossier, APQR, deviation, plant-head, validation/audit workflow scaffolding.
- FastAPI endpoints backed by demo/sample data that run locally without AWS credentials.

## Quick start (local sandbox)

```bash
python -m pip install -e '.[dev]'
pytest -q
uvicorn aeros.kernel.api.main:app --reload
```

## Full system guide

Start with the consolidated end-to-end guide:

- `docs/runbooks/00_FULL_SYSTEM_TEST_AND_DEMO_GUIDE.md`

## Quick start (AWS dev cell)

1. Read `docs/runbooks/00_start_here.md`.
2. Review `docs/architecture/greengrass_v2_edge_gateway.md`.
3. Complete `docs/runbooks/02_aws_account_prerequisites.md`.
4. Bootstrap via `docs/runbooks/03_aws_dev_cell_bootstrap.md`.
5. Plan/apply safely using `docs/runbooks/04_terraform_deploy_dev.md`.
6. Use `docs/runbooks/08_teardown_and_cost_control.md` to clean up and control spend.

## Learning + build playbook

- `docs/learning/phase_3_ontology_learning_map.md`
- `docs/learning/phase_4_assurance_engines_learning_map.md`
- `docs/learning/phase_5_control_plane_learning_map.md`
- `docs/runbooks/09_phase_3_to_5_demo.md`
- `specs/008_enterprise_32_week_roadmap.md`

## Compliance language

This solution is designed to support 21 CFR Part 11 / GxP controls, validation evidence,
auditability, electronic-record integrity, and customer CSV. It does not claim automatic compliance.
