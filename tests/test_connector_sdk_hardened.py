from aeros.kernel.connectors import ConnectorCapability, ConnectorManifest, default_connector_registry


def test_connector_manifest_sets_default_capabilities():
    manifest = ConnectorManifest(
        connector_id="demo-connector",
        connector_type="demo",
        version="0.1.0",
        tenant_id="acme",
        site_id="hyd-01",
        source_system="demo",
    )

    assert ConnectorCapability.CONNECT in manifest.capabilities
    assert ConnectorCapability.EMIT in manifest.capabilities


def test_connector_registry_registration_and_discovery():
    registry = default_connector_registry()

    connectors = registry.list_connectors()
    discovery = registry.discover()

    assert any(connector["connector_id"] == "historian-aveva-pi" for connector in connectors)
    assert any(item["connector_id"] == "qms-veeva-vault" for item in discovery)
