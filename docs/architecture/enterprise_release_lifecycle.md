# Enterprise Release Lifecycle (Phase 1 / Week 4)

1. PR validation (`ci.yml`)
2. Manual infra plan (`terraform-plan.yml`)
3. Protected deployment (`deploy-dev.yml`)
4. Validation evidence collection
5. Promotion gate to QA/prod-cell workflows

Delivery uses GitHub OIDC role assumption (no long-lived cloud keys).
