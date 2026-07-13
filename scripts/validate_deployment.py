#!/usr/bin/env python3
"""Post-deployment smoke and parity validation for customer tenants.

Usage:
  python scripts/validate_deployment.py --environment qa \
    --target acme_pharma=https://acme.qa.example \
    --target nova_bio=https://nova.qa.example

The validator checks only domain-safe control-plane responses. It verifies every
configured site is present, preventing a deployment that silently drops a site.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aeros.kernel.tenancy.parity import load_parity_manifest, validate_parity_manifest


def parse_targets(values: list[str]) -> dict[str, str]:
    targets: dict[str, str] = {}
    for value in values:
        tenant, separator, url = value.partition("=")
        if not separator or not tenant or not url:
            raise ValueError(f"target must be TENANT=URL, got {value!r}")
        targets[tenant] = url.rstrip("/")
    return targets


def request_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(f"{url} returned HTTP {response.status}")
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"deployment validation request failed for {url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{url} returned a non-object JSON payload")
    return payload


def validate_tenant(base_url: str, expected_sites: list[dict[str, Any]]) -> list[str]:
    problems: list[str] = []
    payload = request_json(f"{base_url}/cp/floormap")
    actual_by_id = {site.get("site_id"): site for site in payload.get("sites", [])}
    for expected in expected_sites:
        site_id = expected["site_id"]
        actual = actual_by_id.get(site_id)
        if actual is None:
            problems.append(f"{base_url}: missing site {site_id}")
            continue
        if actual.get("site_label") != expected.get("site_label"):
            problems.append(
                f"{base_url}: site {site_id} label mismatch "
                f"({actual.get('site_label')!r} != {expected.get('site_label')!r})"
            )
        layers = actual.get("layers", [])
        if not layers or not any(layer.get("nodes") for layer in layers):
            problems.append(f"{base_url}: site {site_id} has no topology nodes")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", choices=("local", "dev", "qa", "prod"), required=True)
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="Tenant endpoint in TENANT=URL form; repeat for each customer tenant.",
    )
    args = parser.parse_args()

    manifest = load_parity_manifest(args.environment)
    parity_problems = validate_parity_manifest(manifest)
    if parity_problems:
        for problem in parity_problems:
            print(f"PARITY ERROR: {problem}", file=sys.stderr)
        return 2

    targets = parse_targets(args.target)
    if not targets:
        raw_targets = os.environ.get("AREOS_DEPLOYMENT_TARGETS")
        if raw_targets:
            targets = {key: value.rstrip("/") for key, value in json.loads(raw_targets).items()}
    expected_by_tenant = {
        company["tenant_id"]: company["sites"]
        for company in manifest["companies"]
    }
    missing_targets = sorted(set(expected_by_tenant) - set(targets))
    if missing_targets:
        print(f"missing deployment targets for: {', '.join(missing_targets)}", file=sys.stderr)
        return 2

    problems: list[str] = []
    for tenant_id, expected_sites in expected_by_tenant.items():
        print(f"[validate] {args.environment}/{tenant_id} -> {targets[tenant_id]}")
        try:
            problems.extend(validate_tenant(targets[tenant_id], expected_sites))
        except RuntimeError as exc:
            problems.append(str(exc))

    if problems:
        for problem in problems:
            print(f"VALIDATION ERROR: {problem}", file=sys.stderr)
        return 1
    print(f"Deployment validation passed for {len(expected_by_tenant)} tenants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
