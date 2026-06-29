from __future__ import annotations

import json
from pathlib import Path

from aeros.kernel.connectors.sdk import BaseConnector


def generate_connector_validation_pack(connector: BaseConnector, output_root: str | Path) -> dict:
    root = Path(output_root) / connector.manifest.connector_id
    root.mkdir(parents=True, exist_ok=True)
    validation = connector.validate_contract()
    sample_output = connector.pull()[:5]

    files = {
        "manifest.json": connector.manifest.model_dump(mode="json"),
        "data_contract.json": [contract.model_dump(mode="json") for contract in connector.manifest.data_contracts],
        "mapping_rules.json": [rule.model_dump(mode="json") for rule in connector.manifest.mapping_rules],
        "validation_report.json": validation.model_dump(mode="json"),
        "sample_output.json": sample_output,
    }
    for name, payload in files.items():
        (root / name).write_text(json.dumps(payload, indent=2))
    return {
        "connector_id": connector.manifest.connector_id,
        "root": str(root),
        "files": {name: str(root / name) for name in files},
        "validation": validation.model_dump(mode="json"),
    }
