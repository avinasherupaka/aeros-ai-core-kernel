from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.workflows.deviation_workbench import build_deviation_queue, create_deviation_draft
from aeros.kernel.workflows.engineering_reliability_board import build_engineering_reliability_board
from aeros.kernel.workflows.plant_head_assurance import build_plant_head_assurance_view
from aeros.kernel.workflows.validation_audit_room import build_validation_audit_room


def _get_bundles():
    return [
        get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression"),
        get_demo_event_bundle("event::api_reactor_temperature_excursion"),
    ]


def test_deviation_draft_has_required_fields():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    draft = create_deviation_draft(bundle.event, bundle.impact, bundle.dossier)
    assert draft.deviation_title
    assert draft.problem_statement
    assert draft.impact_assessment_draft
    assert draft.evidence_checklist
    assert draft.suggested_immediate_containment
    assert draft.human_approval_required is True


def test_deviation_queue_has_due_status():
    bundles = _get_bundles()
    events = [b.event for b in bundles]
    impacts = [b.impact for b in bundles]
    queue = build_deviation_queue(events, impacts)
    for item in queue.queue:
        assert item.due_status in ("urgent", "open", "review_pending", "closed")


def test_engineering_board_has_actions_and_table():
    bundles = _get_bundles()
    board = build_engineering_reliability_board(
        site_id="enterprise_demo",
        events=[b.event for b in bundles],
        reliability_insights=[b.reliability_insight for b in bundles],
    )
    assert board.suggested_engineering_actions
    assert board.asset_recurrence_table


def test_plant_head_has_risk_score_and_summary():
    bundles = _get_bundles()
    view = build_plant_head_assurance_view(
        site_id="enterprise_demo",
        events=[b.event for b in bundles],
        impacts=[b.impact for b in bundles],
        reliability_insights=[b.reliability_insight for b in bundles],
    )
    assert 0.0 <= view.site_risk_score <= 1.0
    assert view.site_risk_tier in ("low", "medium", "high", "critical")
    assert view.executive_summary


def test_validation_audit_room_has_completeness_table():
    bundles = _get_bundles()
    room = build_validation_audit_room(
        site_id="enterprise_demo",
        dossiers=[b.dossier for b in bundles],
        impacts=[b.impact for b in bundles],
    )
    assert room.dossier_completeness_table
    assert room.audit_ready_status
    for event_id, status in room.audit_ready_status.items():
        assert status in ("audit_ready", "not_audit_ready")
