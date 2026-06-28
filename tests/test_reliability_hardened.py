from datetime import timedelta

from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.assurance.reliability_intelligence import MaintenanceRecord, RecurrenceClassification, analyze_recurrence


def test_chronic_recurrence_detected():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    prior_events = []
    for i in range(4):
        e = bundle.event.model_copy(deep=True)
        e.event_id = f"prior-chronic-{i}"
        e.timestamp = bundle.event.timestamp - timedelta(days=i + 2)
        prior_events.append(e)
    insight = analyze_recurrence(bundle.event, prior_events)
    assert insight.classification == RecurrenceClassification.CHRONIC_RECURRENCE
    assert insight.recommended_engineering_actions


def test_post_maintenance_recommended_actions():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    prior = bundle.event.model_copy(deep=True)
    prior.event_id = "prior-001"
    prior.timestamp = bundle.event.timestamp - timedelta(days=3)
    maintenance = [
        MaintenanceRecord(
            work_order_id="WO-PM-001",
            asset_id=bundle.event.asset_id,
            completed_at=bundle.event.timestamp - timedelta(days=1),
            summary="Preventive maintenance completed.",
        )
    ]
    insight = analyze_recurrence(bundle.event, [prior], maintenance_records=maintenance)
    assert insight.classification == RecurrenceClassification.POST_MAINTENANCE_RECURRENCE
    assert any("maintenance effectiveness" in action.lower() for action in insight.recommended_engineering_actions)


def test_similarity_score_nonzero_for_similar_events():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    prior = bundle.event.model_copy(deep=True)
    prior.event_id = "prior-sim-001"
    prior.timestamp = bundle.event.timestamp - timedelta(days=2)
    insight = analyze_recurrence(bundle.event, [prior])
    assert insight.similarity_score > 0.0


def test_recurrence_by_asset_metric():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    insight = analyze_recurrence(bundle.event, [])
    assert bundle.event.asset_id + "::" + bundle.event.metric in insight.recurrence_by_asset_metric
