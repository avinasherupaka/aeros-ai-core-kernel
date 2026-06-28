from aeros.kernel.connectors.manifests import ConnectorHealth, ConnectorManifest, ConnectorMode


def test_connector_manifest_defaults_to_read_only_mode():
    manifest = ConnectorManifest(
        connector_id="file-import-1",
        connector_type="file_import",
        version="0.1.0",
        tenant_id="acme",
        site_id="hyd-01",
        source_system="local_files",
    )

    assert manifest.mode == ConnectorMode.READ_ONLY
    assert manifest.enabled is True


def test_connector_health_contains_status_and_details():
    health = ConnectorHealth(connector_id="opcua-1", status="UP", details={"endpoint": "opc.tcp://localhost:4840"})
    assert health.status == "UP"
    assert health.details["endpoint"] == "opc.tcp://localhost:4840"
