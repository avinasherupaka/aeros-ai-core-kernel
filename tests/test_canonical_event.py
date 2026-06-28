from datetime import datetime, timezone

from aeros.kernel.assurance.canonical_event import (
    DataQuality,
    EventContext,
    EventSeverity,
    RawSourceRecord,
    normalize_raw_source_record,
    promote_to_assurance_event,
)


def test_canonical_event_preserves_required_lineage_fields():
    raw = RawSourceRecord(
        tenant_id="acme",
        site_id="site_01",
        source_system="BMS",
        source_protocol="MQTT",
        connector_id="connector-1",
        trace_id="trace-1",
        record_id="record-1",
        record_type="alarm",
        source_timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        payload={"value": 63.0},
        quality=DataQuality.GOOD,
    )
    canonical = normalize_raw_source_record(
        raw,
        event_id="event-1",
        title="Humidity excursion",
        description="Compression room RH event",
        parameter="relative_humidity",
        observed_value=63.0,
        unit="%RH",
        severity=EventSeverity.HIGH,
        context=EventContext(area_id="compression", batch_id="BATCH-1"),
    )
    assert canonical.tenant_id == "acme"
    assert canonical.lineage.connector_id == "connector-1"
    assert canonical.lineage.source_record_reference == "record-1"
    assert canonical.context.batch_id == "BATCH-1"


def test_assurance_event_promotion_keeps_context_and_evidence_needs():
    raw = RawSourceRecord(
        tenant_id="acme",
        site_id="site_01",
        source_system="EMS",
        source_protocol="OPC_UA",
        connector_id="connector-2",
        trace_id="trace-2",
        record_id="record-2",
        record_type="measurement",
        source_timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
        payload={"value": 9.4},
    )
    canonical = normalize_raw_source_record(
        raw,
        event_id="event-2",
        title="Cold room excursion",
        description="Cold room drift",
        parameter="cold_room_temperature",
        observed_value=9.4,
        unit="°C",
        severity=EventSeverity.CRITICAL,
        context=EventContext(room_id="cold_room_01", product_id="mab_gamma", scenario_id="biotech_cold_room_temperature_excursion"),
    )
    assurance = promote_to_assurance_event(
        canonical,
        assurance_event_id="assurance-2",
        risk_ids=["cold-chain_excursion"],
        required_evidence=["temperature trend", "QA hold decision"],
        confidence=0.88,
    )
    assert assurance.lineage.source_protocol == "OPC_UA"
    assert assurance.context.product_id == "mab_gamma"
    assert assurance.required_evidence == ["temperature trend", "QA hold decision"]
