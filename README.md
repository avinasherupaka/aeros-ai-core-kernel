# Areos AI Core Kernel (AWS-native enterprise foundation)

Areos.ai = **Assurance, Reliability, Efficiency Operating System**.

- Areos is a **system of assurance, not a system of record**.
- Existing systems monitor and store records; Areos connects events to validated state, product impact, and audit evidence.
- AI assists evidence generation; humans approve quality decisions.

## Repository positioning

- **Target runtime (MVP path):** AWS-native tenant-site cell.
- **Local runtime:** developer sandbox, simulator, and test harness.

## What is included

### Phase 1 foundation
- Terraform scaffolding for foundation, evidence lake, observability, tenant-site cell, GitHub OIDC.
- Zero-trust/security/compliance/runbook documentation.
- CI/CD workflows for Python + Terraform and OIDC-based deploy scaffolding.

### Phase 2 backbone
- Terraform scaffolding for IoT Core and SiteWise model seed.
- Greengrass component recipe skeletons.
- Connector SDK foundation (`src/aeros/kernel/connectors`) + tests.

## Quick start (local sandbox)

```bash
python -m pip install -e '.[dev]'
pytest -q
```

## Quick start (AWS dev cell)

1. Read `docs/runbooks/00_start_here.md`.
2. Complete `docs/runbooks/02_aws_account_prerequisites.md`.
3. Bootstrap via `docs/runbooks/03_aws_dev_cell_bootstrap.md`.
4. Plan/apply safely using `docs/runbooks/04_terraform_deploy_dev.md`.
5. Use `docs/runbooks/08_teardown_and_cost_control.md` to clean up and control spend.

## Cost/safety notes

- Keep SiteWise resources disabled by default until approved.
- Use dev-only account and plan-first workflow.
- Prefer GitHub OIDC and AWS SSO over long-lived access keys.

## Compliance language

This solution is designed to support 21 CFR Part 11 / GxP controls, validation evidence,
auditability, and electronic-record integrity. It does not claim automatic compliance.
