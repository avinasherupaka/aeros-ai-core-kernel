# Production environment

Production provisions one isolated VPC per customer company. Each tenant may
contain multiple live manufacturing sites, represented in its tenant topology
and `site_parity.json`.

Synthetic simulation is intentionally blocked in production. Use approved
connector profiles, tenant-scoped Secrets Manager references, and an immutable
container image:

```bash
terraform -chdir=environments/prod init
terraform -chdir=environments/prod validate
terraform -chdir=environments/prod plan -var-file=terraform.tfvars
```

Apply only through the protected deployment workflow, followed by the
post-deployment validation job.
