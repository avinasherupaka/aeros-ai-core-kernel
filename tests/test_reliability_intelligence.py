from datetime import timedelta

from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.assurance.reliability_intelligence import MaintenanceRecord, RecurrenceClassification, analyze_recurrence


def test_reliability_engine_detects_post_maintenance_recurrence():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    prior_events = []
    for index in range(2):
        event = bundle.event.model_copy(deep=True)
        event.event_id = f"prior-{index}"
        event.timestamp = bundle.event.timestamp - timedelta(days=index + 2)
        prior_events.append(event)
    maintenance = [
        MaintenanceRecord(
            work_order_id="WO-123",
            asset_id=bundle.event.asset_id,
            completed_at=bundle.event.timestamp - timedelta(days=1),
            summary="Filter replacement and belt tension adjustment.",
        )
    ]
    insight = analyze_recurrence(bundle.event, prior_events, maintenance_records=maintenance)
    assert insight.classification == RecurrenceClassification.POST_MAINTENANCE_RECURRENCE
    assert insight.recurrence_count == 2
