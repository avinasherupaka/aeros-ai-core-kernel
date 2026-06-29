from aeros.kernel.connectors import default_connector_registry


def test_cmms_connector_normalizes_work_orders():
    connector = default_connector_registry().get("cmms-maximo")

    record = connector.pull()[0]["record"]

    assert record["record_type"] == "cmms_work_order"
    assert record["asset_id"] == "AHU-01"


def test_erp_connector_normalizes_genealogy_records():
    connector = default_connector_registry().get("erp-sap-s4")

    record = connector.pull()[0]["record"]

    assert record["record_type"] == "erp_batch_genealogy"
    assert record["batch_id"] == "BATCH-OSD-2026-001"


def test_lims_connector_normalizes_lab_results():
    connector = default_connector_registry().get("lims-labware")

    record = connector.pull()[0]["record"]

    assert record["record_type"] == "lims_result"
    assert record["sample_id"] == "S-100"
