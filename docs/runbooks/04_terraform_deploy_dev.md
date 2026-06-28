# 04 Terraform Deploy (Dev)

```bash
cd infra/terraform/envs/dev
terraform init
terraform fmt -check -recursive ../..
terraform validate
terraform plan -out tfplan
```

Optional apply:

```bash
terraform apply tfplan
terraform output
```

Safety:
- Keep `enable_sitewise_resources = false` until modeling review is complete.
- Keep work in dev account only.
