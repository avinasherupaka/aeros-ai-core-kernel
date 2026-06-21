# 004 ISA-95 and ISA-88 Domain Model

## ISA-95 hierarchy modeled

Tenant → Enterprise/Site → Area → Room/Work Center → Equipment/Utility Asset.

This hierarchy anchors event location and product impact context.

## ISA-88 hierarchy modeled

Batch → Procedure → Operation → Phase.

Used to map utility anomalies to active manufacturing operations (e.g., compression phase in an OSD batch).

## MVP intention

This model is intentionally lean but production-shaped, so future SiteWise asset models and assurance rules can bind to stable identifiers.
