# 08 Teardown and Cost Control

## Cost controls
- Use dev-only account.
- Keep SiteWise resources disabled by default.
- Use PAY_PER_REQUEST DynamoDB.
- Set CloudWatch retention to 30 days.

## Teardown

```bash
cd infra/terraform/envs/dev
terraform plan -destroy
terraform destroy
```

## Post-teardown checks
- Verify S3 bucket and objects are removed (or intentionally retained).
- Confirm no residual IoT rules/thing resources.
- Confirm no unexpected CloudWatch log growth.
