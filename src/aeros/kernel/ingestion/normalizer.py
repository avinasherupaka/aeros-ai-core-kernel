"""
Measurement normalizer for Areos.

Converts raw source data (from OPC UA, BMS, MQTT, files) into
CanonicalEvents suitable for the event router and assurance engines.

AWS equivalent:
  Lambda function triggered by IoT Rules Engine that normalises
  raw MQTT payloads into a canonical JSON schema before writing
  to the canonical event store (DynamoDB/S3).
"""

from aeros.kernel.models.canonical import CanonicalEvent


def normalize_measurement(raw: dict) -> CanonicalEvent:
    """Wrap a raw measurement dict in a CanonicalEvent."""
    return CanonicalEvent(
        tenant_id=raw["tenant_id"],
        site_id=raw["site_id"],
        event_type="measurement",
        source_system=raw.get("source_system", "unknown"),
        payload=raw,
    )


