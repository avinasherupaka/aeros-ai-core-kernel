from aeros.kernel.ingestion.realtime_contracts import (
    RealtimeSourceType, IngestionMode, SourceSystemEvent,
    RealtimeIngestionEnvelope, IngestionAcknowledgement,
    INGESTION_PRIORITY_ORDER,
)


def test_file_import_is_last_in_priority():
    assert INGESTION_PRIORITY_ORDER[-1] == RealtimeSourceType.FILE_IMPORT_LEGACY


def test_webhook_is_first_in_priority():
    assert INGESTION_PRIORITY_ORDER[0] == RealtimeSourceType.WEBHOOK


def test_source_system_event_construction():
    event = SourceSystemEvent(
        event_id='evt_001',
        source_system='bms',
        source_type=RealtimeSourceType.API_POLLING,
        tenant_id='tenant_a',
        site_id='site_1',
        timestamp='2024-01-15T10:00:00Z',
        parameter='temperature',
        value='26.5',
        unit='degC',
    )
    assert event.schema_version == '1.0'
    assert event.source_type == RealtimeSourceType.API_POLLING


def test_ingestion_modes_include_legacy():
    modes = list(IngestionMode)
    assert IngestionMode.MANUAL_LEGACY in modes
    assert IngestionMode.REALTIME in modes
