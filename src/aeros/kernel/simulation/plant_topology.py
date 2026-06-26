"""
OSD plant topology simulation.

Builds an in-memory representation of a realistic Oral Solid Dosage (OSD) plant:
  acme_pharma → Hyderabad Site → OSD Manufacturing → Compression Room 1
  → AHU-03 (utility) + Tablet Press-01 (production equipment)
  → Active batch: BATCH-OSD-2026-001 (hygrostatin 10 mg tablet)

This file simulates the ISA-95 hierarchy that would live in AWS IoT SiteWise
asset models in the target AWS architecture.

Run directly:
    python -m aeros.kernel.simulation.plant_topology
"""

import json

from aeros.kernel.standards.isa88 import BatchRecord
from aeros.kernel.standards.isa95 import Area, Equipment, Room, Site


def build_osd_topology() -> dict:
    tenant_id = "acme_pharma"
    site = Site(tenant_id=tenant_id, site_id="hyd_site_01", enterprise_id="acme_enterprise", name="Hyderabad Site", country="India", timezone="Asia/Kolkata")
    area = Area(tenant_id=tenant_id, site_id=site.site_id, area_id="osd_manufacturing", name="OSD Manufacturing", area_type="osd_manufacturing")
    room = Room(
        tenant_id=tenant_id,
        site_id=site.site_id,
        area_id=area.area_id,
        room_id="compression_room_1",
        name="Compression Room 1",
        room_class="Grade_D",
        gmp_critical=True,
    )
    ahu = Equipment(
        tenant_id=tenant_id,
        site_id=site.site_id,
        area_id=area.area_id,
        room_id=room.room_id,
        equipment_id="ahu_03",
        equipment_type="ahu",
        tag_prefix="BMS.HYD.OSD.CR1.AHU03",
        description="AHU serving Compression Room 1 — controls temperature, humidity, and differential pressure",
    )
    press = Equipment(
        tenant_id=tenant_id,
        site_id=site.site_id,
        area_id=area.area_id,
        room_id=room.room_id,
        equipment_id="tablet_press_01",
        equipment_type="tablet_press",
        tag_prefix="MES.HYD.OSD.CR1.PRESS01",
        description="Tablet press for OSD compression operations",
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
        area_id=area.area_id,
        room_id=room.room_id,
        equipment_id=press.equipment_id,
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


if __name__ == "__main__":
    topology = build_osd_topology()
    print(json.dumps(topology, indent=2))
    print("\n--- Summary ---")
    print(f"Tenant      : {topology['tenant_id']}")
    print(f"Site        : {topology['site']['name']} ({topology['site']['site_id']})")
    print(f"Area        : {topology['area']['name']}")
    print(f"Room        : {topology['room']['name']} [GMP critical: {topology['room']['gmp_critical']}]")
    print(f"AHU         : {topology['utility_asset']['equipment_id']} — {topology['utility_asset']['description']}")
    print(f"Equipment   : {topology['equipment']['equipment_id']} — {topology['equipment']['description']}")
    print(f"Active Batch: {topology['batch']['batch_id']} / {topology['batch']['product_id']}")
