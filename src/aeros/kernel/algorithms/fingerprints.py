"""
Deterministic canonical event fingerprinting.

event_fingerprint = SHA-256(
    tenant_id,
    source_system,
    source_record_id,
    source_timestamp,
    parameter,
    value,
    unit,
    schema_version
)

Same input in any key order → same fingerprint.
"""
import hashlib
import json
from dataclasses import dataclass

FINGERPRINT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class EventFingerprintInput:
    tenant_id: str
    site_id: str
    source_system: str
    source_record_id: str
    source_timestamp: str  # ISO-8601 string for stable serialization
    parameter: str
    value: str  # str for stable serialization (caller converts float→str)
    unit: str
    schema_version: str = FINGERPRINT_SCHEMA_VERSION


def compute_event_fingerprint(fp_input: EventFingerprintInput) -> str:
    """Compute SHA-256 fingerprint. Canonical JSON: sorted keys, no whitespace."""
    canonical = {
        "schema_version": fp_input.schema_version,
        "tenant_id": fp_input.tenant_id,
        "site_id": fp_input.site_id,
        "source_system": fp_input.source_system,
        "source_record_id": fp_input.source_record_id,
        "source_timestamp": fp_input.source_timestamp,
        "parameter": fp_input.parameter,
        "value": fp_input.value,
        "unit": fp_input.unit,
    }
    canonical_json = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
