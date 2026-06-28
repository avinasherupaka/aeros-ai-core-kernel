# Tenant-Site Cell Architecture (Phase 1 / Week 2)

Cell identity:
- `tenant_id`
- `site_id`
- `tenant_site_cell_id = <tenant_id>-<site_id>`

Cell resources:
- KMS key (cell scope)
- DynamoDB event metadata table
- CloudWatch tenant/site log group
- Evidence prefix strategy: `tenant=<id>/site=<id>/`

Supports progressive isolation: logical (MVP) -> account/VPC/KMS siloed model (enterprise).
