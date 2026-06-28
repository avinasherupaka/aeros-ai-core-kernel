import json

from aeros.kernel.connectors.file_import_connector import FileImportConnector
from aeros.kernel.connectors.manifests import ConnectorManifest


def _manifest() -> ConnectorManifest:
    return ConnectorManifest(
        connector_id="file-import-1",
        connector_type="file_import",
        version="0.1.0",
        tenant_id="acme",
        site_id="hyd-01",
        source_system="historian_export",
    )


def test_file_import_connector_reads_json_and_adds_lineage(tmp_path):
    payload_path = tmp_path / "sample.json"
    payload_path.write_text(json.dumps({"tag": "room_humidity", "value": 62.1}))

    connector = FileImportConnector(_manifest(), str(payload_path))

    health = connector.health()
    assert health.status == "UP"

    records = connector.pull()
    assert len(records) == 1
    assert records[0]["tenant_id"] == "acme"
    assert records[0]["site_id"] == "hyd-01"
    assert records[0]["record"]["tag"] == "room_humidity"


def test_file_import_connector_reads_csv(tmp_path):
    payload_path = tmp_path / "sample.csv"
    payload_path.write_text("tag,value\nroom_temp,22.0\n")

    connector = FileImportConnector(_manifest(), str(payload_path))
    records = connector.pull()

    assert len(records) == 1
    assert records[0]["record"]["tag"] == "room_temp"
    assert records[0]["record"]["value"] == "22.0"
