from time import perf_counter

from aeros.kernel.ingestion.event_api_connector import EventApiConnector
from aeros.kernel.ingestion.realtime_contracts import RealtimeSourceType, SourceSystemEvent


def test_ingestion_smoke_under_two_seconds_for_100_events():
    connector = EventApiConnector("tenant_a", "site_1")
    start = perf_counter()
    for index in range(100):
        connector.ingest_event(
            SourceSystemEvent(
                event_id=f"perf-{index}",
                source_system="perf_demo",
                source_type=RealtimeSourceType.API_POLLING,
                tenant_id="tenant_a",
                site_id="site_1",
                timestamp="2026-06-01T10:00:00+00:00",
                parameter="temperature",
                value="25.1",
                unit="degC",
            )
        )
    elapsed = perf_counter() - start
    assert elapsed < 2.0
