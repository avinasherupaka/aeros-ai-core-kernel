# Cloud-native Foundation (Phase 1 / Week 1)

Areos runtime target is AWS-native tenant-site cells using managed services first.

Baseline blocks:
- IAM + GitHub OIDC delivery role.
- KMS encryption domains.
- S3 evidence lake.
- CloudWatch logging.
- Tenant/site-scoped metadata storage.

This design is intended to support GxP auditability, electronic-record integrity,
and customer CSV workflows.
