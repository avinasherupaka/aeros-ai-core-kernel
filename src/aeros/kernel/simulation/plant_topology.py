from aeros.kernel.standards.isa88 import BatchRecord
from aeros.kernel.standards.isa95 import Area, Equipment, Room, Site


def build_osd_topology() -> dict:
    tenant_id = "acme_pharma"
    site = Site(tenant_id=tenant_id, site_id="hyd_site_01", enterprise_id="acme_enterprise", name="Hyderabad Site")
    area = Area(tenant_id=tenant_id, site_id=site.site_id, area_id="osd_manufacturing", name="OSD Manufacturing")
    room = Room(
        tenant_id=tenant_id,
        site_id=site.site_id,
        area_id=area.area_id,
        room_id="compression_room_1",
        name="Compression Room 1",
    )
    ahu = Equipment(
        tenant_id=tenant_id,
        site_id=site.site_id,
        area_id=area.area_id,
        room_id=room.room_id,
        equipment_id="ahu_03",
        equipment_type="ahu",
    )
    press = Equipment(
        tenant_id=tenant_id,
        site_id=site.site_id,
        area_id=area.area_id,
        room_id=room.room_id,
        equipment_id="tablet_press_01",
        equipment_type="tablet_press",
    )
    batch = BatchRecord(
        tenant_id=tenant_id,
        site_id=site.site_id,
        batch_id="BATCH-OSD-2026-001",
        product_id="hygrostatin_10mg_tablet",
        procedure_id="proc_osd_compression",
        operation_id="op_compression",
        phase_id="phase_main_compression",
        status="active",
    )

    return {
        "tenant_id": tenant_id,
        "site": site.model_dump(),
        "area": area.model_dump(),
        "room": room.model_dump(),
        "utility_asset": ahu.model_dump(),
        "equipment": press.model_dump(),
        "batch": batch.model_dump(),
    }
