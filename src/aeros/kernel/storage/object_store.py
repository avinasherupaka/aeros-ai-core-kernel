import json
from pathlib import Path


class LocalObjectStore:
    def __init__(self, base_path: str = "artifacts/evidence"):
        self.base_path = Path(base_path)

    def write_json(self, tenant_id: str, site_id: str, relative_path: str, payload: dict) -> Path:
        target = self.base_path / tenant_id / site_id / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target

    def write_markdown(self, tenant_id: str, site_id: str, relative_path: str, content: str) -> Path:
        target = self.base_path / tenant_id / site_id / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target
