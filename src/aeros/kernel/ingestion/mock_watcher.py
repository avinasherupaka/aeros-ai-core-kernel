"""Local mock ingestion watcher for the control plane compose stack."""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aeros.kernel.ingestion.normalizer import normalize_measurement

POLL_INTERVAL_SECONDS = 5
SUPPORTED_JSON_SUFFIXES = {".json", ".jsonl"}


def _iter_artifact_files(artifacts_root: Path) -> list[Path]:
    return sorted(path for path in artifacts_root.rglob("*") if path.is_file())


def _load_json_payload(path: Path) -> Any:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_payload(payload: Any) -> Any:
    if isinstance(payload, dict) and {"tenant_id", "site_id"}.issubset(payload.keys()):
        return normalize_measurement(payload).model_dump(mode="json")
    if isinstance(payload, list):
        return [
            normalize_measurement(item).model_dump(mode="json")
            if isinstance(item, dict) and {"tenant_id", "site_id"}.issubset(item.keys())
            else item
            for item in payload
        ]
    return payload


def _describe_file(path: Path, artifacts_root: Path) -> dict[str, Any]:
    stat = path.stat()
    record: dict[str, Any] = {
        "path": str(path.relative_to(artifacts_root)),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
        "normalized": False,
    }

    if path.suffix in SUPPORTED_JSON_SUFFIXES:
        try:
            payload = _load_json_payload(path)
            record["normalized_payload"] = _normalize_payload(payload)
            record["normalized"] = True
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            record["normalization_error"] = str(exc)

    return record


def _build_manifest(artifacts_root: Path, api_base_url: str) -> dict[str, Any]:
    files = [_describe_file(path, artifacts_root) for path in _iter_artifact_files(artifacts_root)]
    return {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "artifacts_root": str(artifacts_root),
        "api_base_url": api_base_url,
        "file_count": len(files),
        "files": files,
    }


def _manifest_fingerprint(manifest: dict[str, Any]) -> str:
    payload = json.dumps(manifest, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_manifest(cache_root: Path, manifest: dict[str, Any]) -> None:
    cache_root.mkdir(parents=True, exist_ok=True)
    target = cache_root / "normalized_manifest.json"
    target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    artifacts_root = Path(os.getenv("ARTIFACTS_ROOT", "artifacts")).resolve()
    cache_root = Path(os.getenv("ARTIFACTS_CACHE_ROOT", "/data/cache")).resolve()
    api_base_url = os.getenv("API_BASE_URL", "http://api:8000")

    artifacts_root.mkdir(parents=True, exist_ok=True)
    print(f"[mock-watcher] watching {artifacts_root} and writing cache to {cache_root}")

    last_fingerprint = ""
    while True:
        manifest = _build_manifest(artifacts_root, api_base_url)
        fingerprint = _manifest_fingerprint(manifest)
        if fingerprint != last_fingerprint:
            _write_manifest(cache_root, manifest)
            last_fingerprint = fingerprint
            print(f"[mock-watcher] normalized {manifest['file_count']} artifact(s)")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
