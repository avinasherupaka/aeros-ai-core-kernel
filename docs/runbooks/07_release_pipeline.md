# 07 Release Pipeline

## Workflows
- `ci.yml` - Python tests and Terraform fmt/validate checks.
- `terraform-plan.yml` - plan in dev env (manual trigger).
- `deploy-dev.yml` - protected manual deploy using OIDC role.

## OIDC prerequisites

Configure repository/environment variables:
- `AWS_REGION`
- `TERRAFORM_ENV` (default `dev`)
- `AWS_ROLE_ARN_DEV`

No long-lived AWS access keys are required.
