from pathlib import Path

from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.connectors import default_connector_registry
from aeros.kernel.dossiers.apqr import build_apqr_section
from aeros.kernel.ingestion.event_api_connector import EventApiConnector
from aeros.kernel.ingestion.realtime_contracts import RealtimeSourceType, SourceSystemEvent
from aeros.kernel.models.canonical import EventType
from aeros.kernel.ot.mqtt_publisher import MQTTPublisher
from aeros.kernel.data_backbone.bronze_writer import LocalBronzeWriter


def test_live_connectors_are_registered():
    registry = default_connector_registry()
    for connector_id in (
        "historian-ignition-live",
        "qms-veeva-vault-live",
        "erp-sap-s4-odata-live",
        "cmms-infor-eam-live",
        "lims-labware-live",
        "dms-documentum-live",
    ):
        connector = registry.get(connector_id)
        assert connector.health().details["live_mode_enabled"]


def test_mes_pharmasuite_branding_and_source():
    connector = default_connector_registry().get("mes-pharmasuite")
    assert connector.manifest.source_system == "Rockwell PharmaSuite"
    assert connector.pull()[0]["record"]["phase"] == "compression"


def test_event_api_connector_writes_bronze_record(tmp_path: Path):
    connector = EventApiConnector(
        "tenant_a",
        "site_1",
        bronze_writer=LocalBronzeWriter(tmp_path),
    )
    event = SourceSystemEvent(
        event_id="evt_bronze_1",
        source_system="ignition",
        source_type=RealtimeSourceType.API_POLLING,
        tenant_id="tenant_a",
        site_id="site_1",
        timestamp="2026-06-01T10:00:00+00:00",
        parameter="temperature",
        value="38.4",
        unit="degC",
    )
    ack = connector.ingest_event(event)
    assert ack.output_reference.endswith("evt_bronze_1.json")
    assert Path(ack.output_reference).exists()


def test_bioreactor_temperature_scenario_is_lims_alert():
    bundle = get_demo_event_bundle("event::biotech_bioreactor_temperature_excursion")
    assert bundle.event.event_type == EventType.LIMS_RESULT_ALERT


def test_apqr_human_review_statement_is_configurable():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    section = build_apqr_section(
        site_id=bundle.event.site_id,
        events=[bundle.event],
        impacts=[bundle.impact],
        reliability_insights=[bundle.reliability_insight],
        human_review_statement="Configured by tenant quality policy.",
    )
    assert section.human_review_statement == "Configured by tenant quality policy."


def test_mqtt_publisher_defaults_to_qos_1():
    publisher = MQTTPublisher()
    assert publisher.qos == 1
