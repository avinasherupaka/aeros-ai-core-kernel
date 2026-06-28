# 06 SiteWise Model Deploy

Default mode is scaffold-only (`enable_sitewise_resources = false`).

To trial model creation in sandbox:

1. Set `enable_sitewise_resources = true` in `terraform.tfvars`.
2. Run `terraform plan` and inspect SiteWise resources.
3. Apply in dev only.
4. Capture output/model IDs for validation evidence.

If resources are not enabled, use `artifacts/sitewise/osd_sitewise_models.example.json` as model template.
