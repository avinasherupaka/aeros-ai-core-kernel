#!/usr/bin/env python3
"""Validate all environment parity manifests and tenant configuration folders."""

from __future__ import annotations

from pathlib import Path

from aeros.kernel.tenancy.parity import load_parity_manifest, validate_parity_manifest
from aeros.kernel.tenancy.validation import validate_tenant


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems: list[str] = []

    for environment in ("local", "dev", "qa", "prod"):
        manifest = load_parity_manifest(environment, root / "environments")
        problems.extend(
            f"{environment}/site_parity.json: {problem}"
            for problem in validate_parity_manifest(manifest)
        )

    for tenant_dir in sorted((root / "tenants").iterdir()):
        if not (tenant_dir / "tenant.json").exists():
            continue
        problems.extend(
            f"{tenant_dir.relative_to(root)}: {problem}"
            for problem in validate_tenant(tenant_dir)
        )

    if problems:
        for problem in problems:
            print(f"CONFIG ERROR: {problem}")
        return 1
    print("Environment parity and tenant configurations are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
