# Week 01 — Domain Model and Plant Topology

## Learning goal

Understand the ISA-95 and ISA-88 standards that structure how pharma plants are
modelled digitally. These are the *identifiers and relationships* that Areos uses
to anchor every event, measurement, and piece of evidence.

---

## Why this matters for Dendrix

When an AHU humidity tag crosses the action limit, Areos must answer:
- **Where** is this? (Site → Area → Room)
- **What asset** generated the signal? (AHU-03)
- **What is running?** (Batch BATCH-OSD-2026-001, operation: compression)
- **What product is at risk?** (Hygrostatin 10 mg tablet)
- **Who owns the data?** (Tenant: acme_pharma)

Without the domain model, you have a number (63 %RH). With it, you have context.

---

## ISA-95: Plant hierarchy

ISA-95 Part 1/2 defines a hierarchy for enterprise/plant data exchange.

```
Tenant (Areos extension)
  └── Enterprise (e.g., Acme Pharma Global)
        └── Site (e.g., Hyderabad)
              └── Area (e.g., OSD Manufacturing)
                    └── Room (e.g., Compression Room 1)
                          ├── Utility Asset (e.g., AHU-03)
                          └── Production Equipment (e.g., Tablet Press 01)
```

In AWS this maps to the **SiteWise asset hierarchy**. Locally it maps to the
Python models in `src/aeros/kernel/standards/isa95.py`.

### Code

```python
from aeros.kernel.standards.isa95 import Enterprise, Site, Area, Room, Equipment

site = Site(tenant_id="acme_pharma", site_id="hyd_site_01",
            enterprise_id="acme_enterprise", name="Hyderabad Site")
room = Room(tenant_id="acme_pharma", site_id="hyd_site_01",
            area_id="osd_manufacturing", room_id="compression_room_1",
            name="Compression Room 1", gmp_critical=True)
```

Note that **every model carries `tenant_id` and `site_id`**. This is intentional —
multi-tenancy and site isolation are first-class concerns in Areos.

---

## ISA-88: Batch/process model

ISA-88 Part 1 defines a batch process model used to describe what is being
manufactured at any point in time.

```
BatchRecord
  → Procedure (e.g., OSD tablet compression procedure)
      → Operation (e.g., compression operation)
          → Phase (e.g., main compression phase)
```

During the active batch, if a utility anomaly occurs, Areos links:
`utility event → room → batch → product → quality risk`

### Code

```python
from aeros.kernel.standards.isa88 import BatchRecord

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
```

---

## OSD plant simulation

`simulation/plant_topology.py` builds the complete topology in memory.

```bash
python -m aeros.kernel.simulation.plant_topology
```

This is the local equivalent of querying the AWS IoT SiteWise asset hierarchy API.

---

## Key concepts from the shop floor

**OSD (Oral Solid Dosage)**: tablets, capsules. This is the most common pharma
manufacturing category. Compression rooms are particularly humidity-sensitive
because many tablet formulations are hygroscopic (absorb moisture).

**Hygroscopic product**: A product that absorbs water from the air. For tablets
like Hygrostatin, excess humidity during compression can cause:
- Capping and lamination (tablet breaking)
- Sticking to the punch (yield loss)
- Chemical degradation (potency/purity impact)
- Failed dissolution test

**AHU (Air Handling Unit)**: The HVAC component that controls temperature,
humidity (relative humidity, %RH), and differential pressure in a GMP room.

**Grade D / ISO 8**: GMP room classification. Compression rooms are typically
Grade D, which has environmental monitoring requirements.

**Action limit**: The threshold above which immediate corrective action is
required. Exceeding it means the batch is potentially at risk and a deviation
investigation may be mandatory.

---

## Run / test

```bash
python -m aeros.kernel.simulation.plant_topology
pytest tests/test_domain_models.py -v
```

---

## AWS equivalent (target architecture)

| Local model | AWS service | Notes |
|---|---|---|
| `Site`, `Area`, `Room`, `Equipment` | SiteWise AssetModel + Asset | Hierarchy in SiteWise portal |
| `BatchRecord` | DynamoDB table or SiteWise metadata | Batch context linked to asset |
| `build_osd_topology()` | SiteWise `ListAssets` API | Returns the hierarchy tree |
