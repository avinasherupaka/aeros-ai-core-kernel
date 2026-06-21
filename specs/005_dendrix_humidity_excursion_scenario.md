# 005 Dendrix Humidity Excursion Scenario

Scenario: OSD compression room humidity exceeds action limit during compression for 22 minutes.

Context in MVP:
- Tenant: `acme_pharma`
- Site: `hyd_site_01`
- Area: `osd_manufacturing`
- Room: `compression_room_1`
- Utility asset: `ahu_03`
- Equipment: `tablet_press_01`
- Product: `hygrostatin_10mg_tablet`
- Batch: `BATCH-OSD-2026-001`

Expected assurance flow:
1. Detect state-of-control breach.
2. Link to active room/equipment/batch/product context.
3. Attach prior similar deviation and recent maintenance evidence.
4. Produce human-reviewable impact narrative and dossier payload.
