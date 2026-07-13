# Multi-Tenant, Config-Driven Architecture

> How Aeros transitions from a hardcoded single-site setup to a modular,
> config-driven, multi-environment framework — **without** forking the core.

## 1. Design goals

| Goal | How it's met |
|------|--------------|
| **Core is client-agnostic** | No tenant/site identifiers in `src/`. Identity arrives only via `AREOS_TENANT`. |
| **Uniform schema across tiers** | The same `site_topology.json` / `connectors.json` schema is used locally and in AWS. |
| **Plug & play onboarding** | Add a `tenants/<id>/` folder + one tfvars entry. No code changes. |
| **Strict data tenancy** | Bridge-network-per-tenant locally; VPC-per-tenant in AWS. |
| **Secrets never in git** | `secrets.map.json` holds *references* (ARNs), resolved at runtime. |

## 2. Directory model (additive — existing paths preserved)

```
aeros-ai-core-kernel/
├── src/                         # CORE (environment- & client-agnostic)
│   └── aeros/kernel/
│       ├── api/                 # FastAPI control plane
│       ├── data_backbone/       # Lakehouse + graph store
│       └── tenancy/             # Tenant resolution, validation, and parity checks
├── artifacts/config/            # Built-in single-site fallback config
├── tenants/                     # NEW: per-tenant config (data, not code)
│   ├── README.md
│   ├── acme_pharma/             # Two parity sites: green + yellow
│   └── nova_bio/                # One parity site: red
└── environments/                # NEW: orchestration per environment
    ├── local/                   # Docker Compose multi-tenant stack
    ├── dev/                     # AWS Terraform + digital-twin validation
    ├── qa/                      # Isolated release-candidate validation
    └── prod/                    # Isolated live customer deployment
```

> The core lives in `src/` and is treated as the "/core" module described in the
> overhaul brief. `tenants/` and `environments/` are additive; nothing in `src/`
> was restructured, so existing single-site behaviour is 100% preserved.

## 3. Runtime resolution flow

```
        boot
         │
         ▼
   AREOS_TENANT set? ──no──►  use artifacts/config/  (single-site fallback)
         │ yes
         ▼
   tenancy.tenant_config_root()
         │   resolves ${AREOS_TENANTS_DIR}/<tenant>/config
         ▼
   _cp_config_path("site_topology.json")   # tenant dir is first search root
         │
         ▼
   /cp/floormap, /cp/backbone/status, ...  # serve tenant-scoped data
```

Key code:

- `src/aeros/kernel/tenancy/loader.py` — `active_tenant_id()`,
  `tenant_config_root()`, `resolve_tenant_config()`, `tenant_metadata()`.
- `src/aeros/kernel/tenancy/validation.py` — `validate_tenant()` (schema +
  referential integrity + "no committed secrets" checks).
- `src/aeros/kernel/api/main.py` — `_cp_config_path()` now searches the tenant
  config dir first; `_cp_site_topology_config()` caches per-tenant.

## 4. The uniform config schema

Each tenant folder is identical in shape (see `tenants/README.md`):

```
tenants/<id>/
├── tenant.json            # id, display_name, region, tier, compliance_scope
├── config/site_topology.json   # ISA-95 L0–L4 nodes + data-flow edges
├── connectors.json        # one entry per live feed (protocol, endpoint, secret_ref)
├── secrets.map.json       # secret_ref -> secure-store ARN (references only)
└── tests/test_<tenant>_config.py # validates THIS tenant pre-deploy
```

Because the schema is uniform, the **core APIs, data backbone, and UI configure
themselves** from whichever tenant is active — no per-tenant branching.

## 5. Isolation model

| Layer | Local (`environments/local`) | AWS dev (`environments/dev`) |
|-------|------------------------------|------------------------------|
| Network | One bridge network per tenant | One **VPC** per tenant (non-overlapping CIDRs) |
| Data store | One Postgres container per tenant | Per-tenant DB inside the tenant VPC |
| Secrets | Local env files | Per-tenant Secrets Manager scope `<id>/*` |
| Compute | `api-a`, `api-b` containers | Fargate service per tenant VPC |
| Image | Identical core image | Identical core image |

## 6. Environment and site parity

Every environment carries the same parity matrix in
`environments/<stage>/site_parity.json`, so UI, API, and deployment validation
exercise the same multi-company shape before production:

| Company / tenant | Site | Simulated status |
|---|---|---|
| Acme Pharma (`acme_pharma`) | Hyderabad Plant | Green |
| Acme Pharma (`acme_pharma`) | Pune Plant | Yellow |
| Nova Bio (`nova_bio`) | Boston Biologics Campus | Red |

- **Local** uses `AREOS_DEMO_HEALTH=1` to render the fixed green/yellow/red map
  states and Docker Compose parity services on ports 8030 and 8040.
- **Dev and QA** use the deterministic `scripts/simulate_digital_twin.py`
  producer for near-real-time data-pipeline integration checks.
- **Prod** rejects synthetic simulation and accepts only approved
  tenant-scoped live-system/digital-twin connector profiles.

`scripts/validate_environment_configs.py` validates all parity manifests and
tenant configs in CI. `scripts/validate_deployment.py` runs after deployment,
calls each tenant's `/cp/floormap`, and fails the release if a configured site
is missing, mislabeled, or has no topology nodes.

## 7. Validation & CI gate

Before any deploy, run the tenant's own suite:

```bash
AREOS_TENANT=acme_pharma PYTHONPATH=src pytest tenants/acme_pharma/tests -q
```

`validate_tenant()` fails the build on: missing files, invalid ISA-95 levels,
unknown node kinds, dangling flow endpoints, connector/secret mismatches, or any
literal (non-reference) secret value.

## 8. Onboarding checklist (plug & play)

1. `cp -r tenants/acme_pharma tenants/<new_id>` and edit the config blocks.
2. `pytest tenants/<new_id>/tests -q`.
3. **Local:** add an `api-*/ui-*/postgres-*` block + network in
   `environments/local/docker-compose.multi.yml`.
4. **AWS:** add an entry (with a fresh CIDR) to
   `environments/dev/tenants.auto.tfvars` and `terraform apply`.
