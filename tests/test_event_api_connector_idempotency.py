from aeros.kernel.ingestion.realtime_contracts import RealtimeSourceType, SourceSystemEvent
from aeros.kernel.ingestion.event_api_connector import EventApiConnector


def _make_event(**overrides):
    defaults = dict(
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
    return SourceSystemEvent(**{**defaults, **overrides})


def test_first_ingestion_not_duplicate():
    connector = EventApiConnector('tenant_a', 'site_1')
    ack = connector.ingest_event(_make_event())
    assert not ack.is_duplicate
    assert ack.accepted


def test_second_ingestion_is_duplicate():
    connector = EventApiConnector('tenant_a', 'site_1')
    connector.ingest_event(_make_event())
    ack2 = connector.ingest_event(_make_event())
    assert ack2.is_duplicate


def test_different_event_ids_not_duplicate():
    connector = EventApiConnector('tenant_a', 'site_1')
    connector.ingest_event(_make_event(event_id='evt_001'))
    ack2 = connector.ingest_event(_make_event(event_id='evt_002'))
    assert not ack2.is_duplicate


def test_processed_and_duplicate_counts():
    connector = EventApiConnector('tenant_a', 'site_1')
    connector.ingest_event(_make_event())
    connector.ingest_event(_make_event())
    connector.ingest_event(_make_event(event_id='evt_002'))
    assert connector.processed_count() == 3
    assert connector.duplicate_count() == 1


def test_fingerprint_is_deterministic_across_connectors():
    c1 = EventApiConnector('tenant_a', 'site_1')
    c2 = EventApiConnector('tenant_a', 'site_1')
    event = _make_event()
    ack1 = c1.ingest_event(event)
    ack2 = c2.ingest_event(event)
    assert ack1.fingerprint == ack2.fingerprint
