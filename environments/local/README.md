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
| `pharma_co_a` (Aurora)    | http://localhost:8010 | http://localhost:3010 | `tenant-a-net` |
| `pharma_co_b` (Nexus Bio) | http://localhost:8020 | http://localhost:3020 | `tenant-b-net` |

Each tenant runs on its **own bridge network** with its **own Postgres and cache
volume** — no shared L2 network. This mirrors the VPC-per-tenant isolation used in
`environments/dev` (AWS).

## How tenant selection works

The API mounts the repo `tenants/` folder read-only at `/tenants` and reads
`AREOS_TENANT`. On boot it resolves `tenants/<AREOS_TENANT>/config/site_topology.json`
(and connectors/secrets maps). If `AREOS_TENANT` is unset, it falls back to the
built-in single-site config under `artifacts/config/`.

Verify a running tenant:

```bash
curl -s localhost:8010/cp/floormap | jq '.sites[0].site_label'   # "Aurora Pharma - Hyderabad"
curl -s localhost:8020/cp/floormap | jq '.sites[0].site_label'   # "Nexus Bio - Boston"
```

## Validate a tenant before starting it

```bash
AREOS_TENANT=pharma_co_a PYTHONPATH=src pytest tenants/pharma_co_a/tests -q
AREOS_TENANT=pharma_co_b PYTHONPATH=src pytest tenants/pharma_co_b/tests -q
```

## Add a third facility (plug & play)

1. `cp -r tenants/pharma_co_a tenants/pharma_co_c` and edit the config blocks.
2. Copy `.env.pharma_co_a` → `.env.pharma_co_c` and update `AREOS_TENANT`.
3. Duplicate the `api-*` / `ui-*` / `postgres-*` service block in
   `docker-compose.multi.yml`, add a `tenant-c-net`, and pick fresh host ports.
4. `pytest tenants/pharma_co_c/tests -q`, then `docker compose ... up`.
