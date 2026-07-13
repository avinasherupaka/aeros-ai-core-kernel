#!/usr/bin/env python3
"""Emit deterministic near-real-time digital-twin telemetry for dev and QA.

Local mode writes JSONL to stdout. Dev/QA can additionally POST each event to
AREOS_SIMULATOR_TARGET_URL. Production is intentionally rejected so synthetic
telemetry cannot be connected to a live tenant by accident.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_strategy(environment: str) -> dict[str, Any]:
    path = Path("environments") / environment / "data_strategy.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_reading(site_id: str, health_state: str, rng: random.Random) -> dict[str, Any]:
    baseline = {"green": 45.0, "yellow": 61.0, "red": 78.0}[health_state]
    return {
        "event_type": "digital_twin.telemetry",
        "source": "aeros-digital-twin",
        "synthetic": True,
        "site_id": site_id,
        "metric": "relative_humidity",
        "value": round(baseline + rng.uniform(-1.5, 1.5), 3),
        "unit": "%",
        "health_state": health_state,
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }


def publish(target_url: str, tenant_id: str, reading: dict[str, Any]) -> None:
    payload = json.dumps(reading).encode("utf-8")
    request = Request(
        target_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Areos-Tenant": tenant_id,
            "X-Areos-Synthetic": "true",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError(f"simulator target returned HTTP {response.status}")
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"simulator target request failed: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", choices=("local", "dev", "qa", "prod"), required=True)
    parser.add_argument("--once", action="store_true", help="Emit one reading per configured site.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    strategy = load_strategy(args.environment)
    if strategy["mode"] == "live_system_only":
        raise SystemExit("Synthetic digital-twin simulation is disabled for prod.")

    target_url = os.environ.get("AREOS_SIMULATOR_TARGET_URL")
    if strategy.get("allow_network_publish") and target_url is None:
        raise SystemExit("AREOS_SIMULATOR_TARGET_URL is required for dev/qa simulation.")

    health_states = strategy.get("health_states", {
        "acme_hyd_01": "green",
        "acme_pun_02": "yellow",
        "nova_bos_01": "red",
    })
    rng = random.Random(args.seed)
    interval = float(strategy.get("interval_seconds") or 1)

    while True:
        for tenant_id in strategy["tenants"]:
            tenant_sites = {
                site_id: state
                for site_id, state in health_states.items()
                if site_id.startswith("acme_") and tenant_id == "acme_pharma"
                or site_id.startswith("nova_") and tenant_id == "nova_bio"
            }
            for site_id, health_state in tenant_sites.items():
                reading = build_reading(site_id, health_state, rng)
                if target_url and strategy.get("allow_network_publish"):
                    publish(target_url, tenant_id, reading)
                print(json.dumps({"tenant_id": tenant_id, **reading}), flush=True)
        if args.once:
            return 0
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
