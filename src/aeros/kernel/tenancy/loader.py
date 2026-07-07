"""Resolve tenant-scoped configuration files from environment variables.

This module contains no client-specific knowledge. It only knows *how* to find a
tenant's config directory; the actual layout, connectors, and secrets mappings
live entirely in data under the tenants root.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

_DEFAULT_TENANTS_DIR = "tenants"


def active_tenant_id() -> Optional[str]:
    """Return the tenant id selected for this process, or ``None`` for single-site."""
    tenant = os.environ.get("AREOS_TENANT", "").strip()
    return tenant or None


def _tenants_root() -> Path:
    """Root directory holding per-tenant config folders."""
    return Path(os.environ.get("AREOS_TENANTS_DIR", _DEFAULT_TENANTS_DIR))


def _candidate_tenant_roots(tenant: str) -> list[Path]:
    """Possible on-disk locations for a tenant folder, most specific first."""
    root = _tenants_root()
    here = Path(__file__).resolve()
    # repo root = .../src/aeros/kernel/tenancy/loader.py -> parents[4]
    repo_root = here.parents[4] if len(here.parents) >= 5 else Path.cwd()
    return [
        root / tenant,
        Path.cwd() / root / tenant,
        repo_root / _DEFAULT_TENANTS_DIR / tenant,
    ]


def tenant_config_root() -> Optional[str]:
    """Return the ``<tenant>/config`` directory for the active tenant, if any.

    The returned path is suitable to prepend to a config-file search path. Returns
    ``None`` when no tenant is selected (single-site fallback) or the tenant folder
    cannot be located.
    """
    tenant = active_tenant_id()
    if not tenant:
        return None
    for base in _candidate_tenant_roots(tenant):
        config_dir = base / "config"
        if config_dir.is_dir():
            return str(config_dir)
    return None


def resolve_tenant_config(filename: str) -> Optional[Path]:
    """Return the path to ``filename`` inside the active tenant's config dir.

    Returns ``None`` if there is no active tenant or the file is absent, so callers
    can transparently fall back to the built-in single-site configuration.
    """
    config_root = tenant_config_root()
    if not config_root:
        return None
    candidate = Path(config_root) / filename
    return candidate if candidate.exists() else None


def tenant_metadata() -> dict[str, Any]:
    """Return the active tenant's ``tenant.json`` metadata (empty if none)."""
    tenant = active_tenant_id()
    if not tenant:
        return {}
    for base in _candidate_tenant_roots(tenant):
        meta = base / "tenant.json"
        if meta.exists():
            with open(meta, "r", encoding="utf-8") as handle:
                return json.load(handle)
    return {}


def list_tenants() -> list[str]:
    """List available tenant ids under the tenants root (for tooling/CLI)."""
    root = _tenants_root()
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if (p / "config").is_dir())
