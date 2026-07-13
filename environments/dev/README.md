# environments/dev — AWS Tenant-Isolated Infrastructure (IaC)

Terraform that provisions the Aeros control plane into an **isolated VPC per
tenant**. This enforces strict data tenancy, security compliance, and network
segregation: tenants share no network boundary.

```
environments/dev/
├── main.tf                     # Root: fans out one tenant_vpc module per tenant
├── variables.tf                # Region, image, tenants map
├── outputs.tf                  # Per-tenant endpoints + VPC IDs
├── tenants.auto.tfvars         # The tenant fleet (CIDRs, task counts)
└── modules/tenant_vpc/         # Reusable isolated-VPC + control-plane stack
```

## Isolation model

```
        ┌──────────────────────── AWS Dev Account ────────────────────────┐
        │                                                                  │
        │   VPC 10.10.0.0/16 (acme_pharma)     VPC 10.20.0.0/16 (nova_bio)
        │   ├─ private subnets  ├─ ECS/Fargate  ├─ private subnets  ├─ ECS │
        │   ├─ Secrets: acme/*   │   AREOS_TENANT ├─ Secrets: nova/* │      │
        │   └─ ALB (acme.dev)    │   =acme_pharma └─ ALB (nova.dev)  │      │
        │                                                                  │
        │   No peering. No shared subnets. No shared secret scope.         │
        └──────────────────────────────────────────────────────────────────┘
```

The **same container image** runs in every tenant VPC. Tenant identity is injected
only through the `AREOS_TENANT` environment variable on the ECS task definition;
the core resolves `${AREOS_TENANTS_DIR}/${AREOS_TENANT}/config/...` at runtime.

## Usage

```bash
cd environments/dev
terraform init
terraform plan       # uses AWS creds from your existing dev account profile
terraform apply
```

Configure remote state (S3 + DynamoDB lock) in `main.tf` before real use.

## Secrets handling

- No secret **values** live in Terraform or in `tenants/`.
- Each tenant gets a scoped `aws_secretsmanager_secret` (`<tenant_id>/control-plane`).
- `tenants/<id>/secrets.map.json` maps each connector's `secret_ref` to a secure
  store ARN, resolved by the task role at runtime (least-privilege, per-tenant).

## Onboarding a new facility (config-only)

1. Add `tenants/<new_id>/` (see `tenants/README.md`).
2. Add an entry to `tenants.auto.tfvars` with a **non-overlapping** `vpc_cidr`.
3. `terraform apply` — a new isolated VPC + control plane comes up automatically.

> This skeleton provisions the VPC, subnets, IGW, and tenant secret so it plans
> cleanly. NAT, route tables, ALB, and the ECS service are stubbed as commented
> blocks to be completed against your org's networking/CI standards.
