"""Site-specific config validation for tenant pharma_co_b.

Run before deployment:
    AREOS_TENANT=pharma_co_b pytest tenants/pharma_co_b/tests -q
"""

from pathlib import Path

from aeros.kernel.tenancy.validation import validate_tenant

TENANT_DIR = Path(__file__).resolve().parents[1]


def test_tenant_config_is_valid():
    problems = validate_tenant(TENANT_DIR)
    assert problems == [], "tenant config problems:\n" + "\n".join(problems)


def test_primary_site_present():
    import json

    tenant = json.loads((TENANT_DIR / "tenant.json").read_text())
    topo = json.loads((TENANT_DIR / "config" / "site_topology.json").read_text())
    site_ids = {s["site_id"] for s in topo["sites"]}
    assert tenant["primary_site_id"] in site_ids
