from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.workflows.deviation_workbench import build_deviation_queue
from aeros.kernel.workflows.engineering_reliability_board import build_engineering_reliability_board
from aeros.kernel.workflows.plant_head_assurance import build_plant_head_assurance_view
from aeros.kernel.workflows.validation_audit_room import build_validation_audit_room


def test_workflow_views_provide_non_ui_control_plane_summaries():
    bundles = [
        get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression"),
        get_demo_event_bundle("event::api_reactor_temperature_excursion"),
    ]
    events = [bundle.event for bundle in bundles]
    impacts = [bundle.impact for bundle in bundles]
    insights = [bundle.reliability_insight for bundle in bundles]
    dossiers = [bundle.dossier for bundle in bundles]

    deviation_queue = build_deviation_queue(events, impacts)
    reliability_board = build_engineering_reliability_board(site_id="enterprise_demo", events=events, reliability_insights=insights)
    plant_head = build_plant_head_assurance_view(site_id="enterprise_demo", events=events, impacts=impacts, reliability_insights=insights)
    validation_room = build_validation_audit_room(site_id="enterprise_demo", dossiers=dossiers, impacts=impacts)

    assert len(deviation_queue.queue) == 2
    assert reliability_board.asset_event_counts
    assert plant_head.batch_release_risk_count >= 1
    assert validation_room.evidence_lineage_completeness
