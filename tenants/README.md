# Tenants — Config-Driven, Plug-&-Play Facility Onboarding

Each folder under `tenants/` is a **self-contained, environment-agnostic**
description of one facility (site). The Aeros core reads exactly one tenant at a
time, selected by the `AREOS_TENANT` environment variable. No core code changes
are required to onboard a new facility — you add data, not logic.

## Selecting a tenant

```bash
export AREOS_TENANT=acme_pharma        # which facility this process serves
export AREOS_TENANTS_DIR=tenants       # optional; defaults to ./tenants (or /tenants in containers)
```

If `AREOS_TENANT` is unset, the core falls back to the built-in single-site
config under `artifacts/config/` — existing behaviour is preserved with zero
configuration.

## Uniform schema (identical across all tenants and all tiers)

```
tenants/<tenant_id>/
├── tenant.json               # Tenant metadata (id, display name, region, tier)
├── config/
│   └── site_topology.json    # ISA-95 L0–L4 layout + nodes + flows (Live Floor Map)
├── connectors.json           # Data-backbone connector inventory (IoT / MES / ERP / LIMS…)
├── secrets.map.json          # References to secure stores (NO real secrets in git)
└── tests/
    └── test_<tenant>_config.py # Validates this tenant's config before deployment
```

`config/site_topology.json` uses the **same schema** as
`artifacts/config/site_topology.json` (see `schema_version`). This uniformity is
what makes onboarding "plug & play": fill out the standardized blocks, run the
tenant test suite, and the core APIs / data backbone / UI configure themselves.

## Onboarding a new facility (checklist)

1. Copy an existing tenant folder as a template:
   `cp -r tenants/acme_pharma tenants/<new_tenant_id>`
2. Edit `tenant.json` (id, display name, region, tier).
3. Edit `config/site_topology.json` — layers, nodes, and data-flow edges for the
   facility. Reference each instrumented node's `connector_id`.
4. Edit `connectors.json` — one entry per live feed (protocol, endpoint ref,
   `secret_ref`).
5. Edit `secrets.map.json` — map each `secret_ref` to a secure-store path
   (AWS Secrets Manager / SSM). **Never commit real secrets.**
6. Run the tenant test suite:
   `AREOS_TENANT=<new_tenant_id> pytest tenants/<new_tenant_id>/tests -q`
7. Launch locally via `environments/local/docker-compose.multi.yml`, or deploy to
   an isolated VPC via `environments/dev/`.

## Data tenancy & isolation

- **Local:** each tenant runs as its own compose stack (separate network + volume).
- **AWS dev:** each tenant runs in its **own isolated VPC** (see
  `environments/dev/`), guaranteeing network segregation and strict data tenancy.
