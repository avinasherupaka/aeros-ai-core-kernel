from datetime import datetime, timezone

from aeros.kernel.connectors import ConnectorReplayRequest, default_connector_registry


def test_historian_connector_extracts_and_normalizes_records():
    connector = default_connector_registry().get("historian-aveva-pi")

    records = connector.pull()

    assert len(records) == 3
    assert records[0]["record"]["record_type"] == "parameter_observation"
    assert records[0]["source_lineage"]["read_only"] is True


def test_historian_connector_replay_filters_time_window():
    connector = default_connector_registry().get("historian-aveva-pi")

    result = connector.replay(
        ConnectorReplayRequest(
            start_time=datetime(2026, 6, 1, 10, 5, tzinfo=timezone.utc),
            end_time=datetime(2026, 6, 1, 10, 15, tzinfo=timezone.utc),
        )
    )

    assert result.records_out == 1
    assert result.sample_output[0]["record"]["source_record_id"] == "PI-2"
