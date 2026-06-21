from aeros.kernel.models.canonical import CanonicalEvent


def normalize_measurement(raw: dict) -> CanonicalEvent:
    return CanonicalEvent(
        tenant_id=raw["tenant_id"],
        site_id=raw["site_id"],
        event_type="measurement",
        source_system=raw.get("source_system", "unknown"),
        payload=raw,
    )
