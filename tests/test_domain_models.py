from aeros.kernel.ot.sparkplug_envelope import SparkplugInspiredEnvelope
from aeros.kernel.standards.isa88 import BatchRecord
from aeros.kernel.standards.isa95 import Equipment


def test_isa_models_include_tenant_and_site_context():
    equipment = Equipment(
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        area_id="osd_manufacturing",
        room_id="compression_room_1",
        equipment_id="tablet_press_01",
        equipment_type="tablet_press",
    )
    batch = BatchRecord(
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        batch_id="BATCH-OSD-2026-001",
        product_id="hygrostatin_10mg_tablet",
        procedure_id="proc_osd_compression",
        operation_id="op_compression",
        phase_id="phase_main_compression",
        status="active",
    )
    assert equipment.tenant_id == batch.tenant_id
    assert batch.site_id == "hyd_site_01"


def test_sparkplug_inspired_envelope_fields_present():
    envelope = SparkplugInspiredEnvelope(
        tenant_id="acme_pharma",
        site_id="hyd_site_01",
        edge_node_id="edge_hyd_01",
        device_id="ahu_03",
        metric="relative_humidity",
        value=63.0,
        unit="%RH",
        quality="GOOD",
        sequence=1,
        source_protocol="opcua",
        source_system="bms",
        trace_id="trace-123",
    )
    assert envelope.metric == "relative_humidity"
    assert envelope.source_protocol == "opcua"
