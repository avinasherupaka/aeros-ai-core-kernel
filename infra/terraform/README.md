# Areos Terraform (Phase 1–2 Foundation)

This Terraform tree defines a **safe AWS-native scaffold** for an Areos tenant-site cell.

Design goals:
- Read-only-first OT integration assumptions.
- Lowest-cost defaults where possible.
- Clear separation between reusable modules and environment instantiations.
- Explicitly mark scaffold vs production-hardening TODOs.

## Layout

- `modules/foundation` - account/region metadata and standard tags.
- `modules/evidence_lake` - S3 evidence bucket + optional KMS key.
- `modules/observability` - baseline CloudWatch log groups.
- `modules/iam_github_oidc` - GitHub Actions OIDC role.
- `modules/tenant_site_cell` - tenant/site-scoped metadata plane (KMS, DynamoDB, logs).
- `modules/iot_core` - tenant/site IoT thing/policy/rule scaffold.
- `modules/sitewise` - SiteWise model template outputs and optional resource scaffold.
- `envs/*` - dev/qa/prod-cell-template entrypoints.

## Safe usage

1. Copy `terraform.tfvars.example` to `terraform.tfvars` in the target env.
2. Run `terraform init` and `terraform plan` first.
3. Apply only in a sandbox AWS account after reviewing resources and cost.
4. Use `docs/runbooks/08_teardown_and_cost_control.md` for cleanup.

> This configuration is designed to support 21 CFR Part 11 / GxP controls,
> validation evidence, auditability, and customer CSV. It does not claim
> automatic compliance.
