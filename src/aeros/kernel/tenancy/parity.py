"""Validation helpers for environment/site parity manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_parity_manifest(environment: str, root: str | Path = "environments") -> dict[str, Any]:
    """Load one environment's parity manifest from a controlled repository path."""
    if environment not in {"local", "dev", "qa", "prod"}:
        raise ValueError(f"unsupported environment: {environment}")
    path = Path(root) / environment / "site_parity.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_parity_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return actionable parity errors; an empty list means the manifest is valid."""
    problems: list[str] = []
    environment = manifest.get("environment")
    if environment not in {"local", "dev", "qa", "prod"}:
        problems.append("environment must be local, dev, qa, or prod")

    companies = manifest.get("companies")
    if not isinstance(companies, list) or not companies:
        problems.append("companies must contain at least one company")
        return problems

    company_ids: set[str] = set()
    site_ids: set[str] = set()
    for company in companies:
        company_id = company.get("company_id")
        tenant_id = company.get("tenant_id")
        if not company_id:
            problems.append("company missing company_id")
        elif company_id in company_ids:
            problems.append(f"duplicate company_id: {company_id}")
        else:
            company_ids.add(company_id)
        if not tenant_id:
            problems.append(f"{company_id or 'company'} missing tenant_id")

        sites = company.get("sites")
        if not isinstance(sites, list) or not sites:
            problems.append(f"{company_id or 'company'} must contain at least one site")
            continue
        for site in sites:
            site_id = site.get("site_id")
            if not site_id:
                problems.append(f"{company_id or 'company'} has a site without site_id")
            elif site_id in site_ids:
                problems.append(f"duplicate site_id: {site_id}")
            else:
                site_ids.add(site_id)
            if site.get("health_state") not in {"green", "yellow", "red"}:
                problems.append(f"{site_id or 'site'} health_state must be green, yellow, or red")
            site_tenant_id = site.get("tenant_id", tenant_id)
            if not site_tenant_id:
                problems.append(f"{site_id or 'site'} has no inherited tenant_id")

    if len(company_ids) < 2:
        problems.append("parity manifest must cover at least two companies")
    if len(site_ids) < 3:
        problems.append("parity manifest must cover at least three sites")
    return problems
