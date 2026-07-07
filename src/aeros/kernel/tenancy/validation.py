"""Tenant configuration validation.

Uniform, schema-aware checks so any facility's config can be validated *before*
deployment. Returns a list of human-readable problems; empty list == valid.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_VALID_NODE_KINDS = {
    "sensor", "plc", "opcua", "bms", "scada", "mes", "historian",
    "edge_gateway", "mqtt_broker", "iot_core", "lims", "qms", "erp",
    "cmms", "lakehouse",
}
_VALID_LEVELS = {"L0", "L1", "L2", "L3", "L4"}
_REQUIRED_FILES = ("tenant.json", "config/site_topology.json", "connectors.json", "secrets.map.json")


def _load(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_tenant(tenant_dir: str | Path) -> list[str]:
    """Validate a single tenant folder. Returns a list of problems (empty == ok)."""
    tenant_dir = Path(tenant_dir)
    problems: list[str] = []

    # 1. Required files present
    for rel in _REQUIRED_FILES:
        if not (tenant_dir / rel).exists():
            problems.append(f"missing required file: {rel}")
    if problems:
        return problems  # can't meaningfully continue

    tenant = _load(tenant_dir / "tenant.json")
    topo = _load(tenant_dir / "config" / "site_topology.json")
    connectors_doc = _load(tenant_dir / "connectors.json")
    secrets_doc = _load(tenant_dir / "secrets.map.json")

    tenant_id = tenant.get("tenant_id")
    if not tenant_id:
        problems.append("tenant.json: missing tenant_id")
    if tenant.get("tenant_id") != tenant_dir.name:
        problems.append(
            f"tenant.json tenant_id '{tenant.get('tenant_id')}' does not match folder '{tenant_dir.name}'"
        )

    # 2. Topology structural checks
    sites = topo.get("sites")
    if not sites:
        problems.append("site_topology.json: no sites defined")
        sites = []

    all_node_ids: set[str] = set()
    node_connector_ids: set[str] = set()
    for site in sites:
        for key in ("site_id", "site_label"):
            if not site.get(key):
                problems.append(f"site missing '{key}'")
        levels_seen = set()
        for layer in site.get("layers", []):
            level = layer.get("level")
            levels_seen.add(level)
            if level not in _VALID_LEVELS:
                problems.append(f"invalid ISA-95 level: {level!r}")
            for node in layer.get("nodes", []):
                nid = node.get("id")
                if not nid:
                    problems.append("node missing 'id'")
                    continue
                if nid in all_node_ids:
                    problems.append(f"duplicate node id: {nid}")
                all_node_ids.add(nid)
                if node.get("kind") not in _VALID_NODE_KINDS:
                    problems.append(f"node {nid}: invalid kind {node.get('kind')!r}")
                if node.get("connector_id"):
                    node_connector_ids.add(node["connector_id"])

        # 3. Flow referential integrity
        for flow in site.get("flows", []):
            for endpoint in ("from", "to"):
                ref = flow.get(endpoint)
                if ref not in all_node_ids:
                    problems.append(f"flow {endpoint} references unknown node: {ref}")

    # 4. Connector <-> secret referential integrity
    connectors = connectors_doc.get("connectors", [])
    declared_connector_ids = {c.get("connector_id") for c in connectors}
    secret_keys = set(secrets_doc.get("mappings", {}).keys())
    for conn in connectors:
        cid = conn.get("connector_id")
        if not cid:
            problems.append("connectors.json: connector missing connector_id")
        sref = conn.get("secret_ref")
        if sref and sref not in secret_keys:
            problems.append(f"connector {cid}: secret_ref '{sref}' not in secrets.map.json")

    # 5. Every node connector_id must be declared in connectors.json
    for cid in node_connector_ids:
        if cid not in declared_connector_ids:
            problems.append(f"topology references connector '{cid}' not declared in connectors.json")

    # 6. No real secret values committed (mappings must be references, not literals)
    for key, val in secrets_doc.get("mappings", {}).items():
        if not isinstance(val, str) or not (val.startswith("arn:") or val.startswith("ssm:") or "://" in val):
            problems.append(f"secrets.map.json: '{key}' does not look like a secure-store reference")

    return problems
