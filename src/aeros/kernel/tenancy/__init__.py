"""Tenancy: config-driven, environment-agnostic multi-tenant resolution.

The Aeros core stays entirely tenant- and environment-agnostic. Which facility a
running process serves is selected purely by environment variables at boot:

    AREOS_TENANT       Tenant/site identifier (e.g. "pharma_co_a"). If unset, the
                       core falls back to the built-in single-site configuration
                       under ``artifacts/config`` so existing behaviour is
                       preserved with zero configuration.
    AREOS_TENANTS_DIR  Root directory that holds per-tenant config folders.
                       Defaults to ``tenants`` (repo root) for local development;
                       in containers it is typically mounted at ``/tenants``.

Onboarding a new facility is "plug & play": drop a new folder under the tenants
root that follows the uniform schema (see ``tenants/README.md``) and point
``AREOS_TENANT`` at it. No core code changes are required.
"""

from .loader import (
    active_tenant_id,
    tenant_config_root,
    tenant_metadata,
    resolve_tenant_config,
    list_tenants,
)
from .validation import validate_tenant

__all__ = [
    "active_tenant_id",
    "tenant_config_root",
    "tenant_metadata",
    "resolve_tenant_config",
    "list_tenants",
    "validate_tenant",
]
