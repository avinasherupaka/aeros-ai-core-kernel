# 03 AWS Dev Cell Bootstrap

1. Go to `infra/terraform/envs/dev`.
2. Copy `terraform.tfvars.example` to `terraform.tfvars`.
3. Set unique evidence bucket name.
4. Confirm tenant/site identifiers.
5. Run plan only first.

```bash
cd infra/terraform/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
```

Apply only after explicit review of resources and cost.
