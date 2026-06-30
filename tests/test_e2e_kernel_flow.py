from aeros.kernel.api.main import (
    BedrockRenderDraftBody,
    SimulateEventBody,
    bedrock_render_draft,
    get_connector_registry,
    simulate_ingest_event,
)


def test_e2e_connectors_and_ingestion_flow():
    connectors = get_connector_registry()
    connector_ids = {item["connector_id"] for item in connectors["connectors"]}
    assert "historian-ignition-live" in connector_ids
    assert "mes-pharmasuite" in connector_ids

    ingest = simulate_ingest_event(
        SimulateEventBody(
            source_system="ignition",
            parameter="bioreactor_temperature",
            value="38.4",
            unit="degC",
            event_id="e2e-evt-001",
            timestamp="2026-06-01T10:00:00+00:00",
        )
    )
    assert ingest["accepted"] is True
    assert ingest["is_duplicate"] is False
    assert ingest["processor_version"] == "event_api_connector:1.0"


def test_e2e_bedrock_guardrail_flow():
    response = bedrock_render_draft(
        BedrockRenderDraftBody(
            answer_id="e2e-answer-1",
            rendered_text="System approves batch is released with no human review needed.",
        )
    )
    assert response["guardrail_passed"] is False
    assert response["human_approval_required"] is True
