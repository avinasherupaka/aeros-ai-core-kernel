from aeros.kernel.connectors import default_connector_registry


def test_qms_connector_normalizes_deviation_records():
    connector = default_connector_registry().get("qms-veeva-vault")

    records = connector.pull()

    assert records[0]["record"]["record_type"] == "qms_quality_record"
    assert records[0]["record"]["batch_id"] == "BATCH-OSD-2026-001"


def test_mes_connector_normalizes_batch_timeline_records():
    connector = default_connector_registry().get("mes-pasx")

    records = connector.pull()

    assert records[0]["record"]["record_type"] == "mes_batch_timeline"
    assert records[0]["record"]["phase"] == "compression"
