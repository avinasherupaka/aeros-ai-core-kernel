# environments/local — Multi-Tenant Local Development

Spin up **two isolated sample facilities simultaneously** from local config files.
The core image is identical for every tenant; only `AREOS_TENANT` differs.

## Quick start

```bash
# From the repo root:
docker compose -f environments/local/docker-compose.multi.yml up --build
```

| Tenant                    | API              | UI                | Network        |
|---------------------------|------------------|-------------------|----------------|
| `acme_pharma` (Hyderabad + Pune) | http://localhost:8030 | http://localhost:3030 | `tenant-acme-net` |
| `nova_bio` (Boston) | http://localhost:8040 | http://localhost:3040 | `tenant-nova-net` |

Each tenant runs on its **own bridge network** with its **own writable cache
volume** — no shared L2 network. This mirrors the VPC-per-tenant isolation used
in `environments/dev` (AWS). Add a tenant-local Postgres service only when the
selected deployment profile enables database-backed workflow state.

## How tenant selection works

The API mounts the repo `tenants/` folder read-only at `/tenants` and reads
`AREOS_TENANT`. On boot it resolves `tenants/<AREOS_TENANT>/config/site_topology.json`
(and connectors/secrets maps). If `AREOS_TENANT` is unset, it falls back to the
built-in single-site config under `artifacts/config/`.

Verify a running tenant:

```bash
curl -s localhost:8030/cp/floormap | jq '.sites[].site_label'  # Hyderabad Plant, Pune Plant
curl -s localhost:8040/cp/floormap | jq '.sites[].site_label'  # Boston Biologics Campus
```

## Validate a tenant before starting it

```bash
AREOS_TENANT=acme_pharma PYTHONPATH=src pytest tenants/acme_pharma/tests -q
AREOS_TENANT=nova_bio PYTHONPATH=src pytest tenants/nova_bio/tests -q
```

## Add a third facility (plug & play)

1. `cp -r tenants/acme_pharma tenants/<new_tenant_id>` and edit the config blocks.
2. Add a tenant entry to the Local parity manifest and update `AREOS_TENANT`.
3. Duplicate the `api-*` / `ui-*` service block in
   `docker-compose.multi.yml`, add a `tenant-c-net`, and pick fresh host ports.
4. `pytest tenants/<new_tenant_id>/tests -q`, then `docker compose ... up`.
