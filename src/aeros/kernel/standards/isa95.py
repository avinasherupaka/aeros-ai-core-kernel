"""
ISA-95 Part 1/2 inspired plant hierarchy for Areos.

Hierarchy: Tenant → Enterprise → Site → Area → Room → Equipment/Utility Asset.

This is a read-only domain model.  All identifiers flow downstream into
UNS topics, SiteWise asset models, assurance events, and evidence records.
"""

from pydantic import BaseModel


class Enterprise(BaseModel):
    tenant_id: str
    enterprise_id: str
    name: str


class Site(BaseModel):
    tenant_id: str
    site_id: str
    enterprise_id: str
    name: str
    country: str = ""
    timezone: str = "UTC"


class Area(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    name: str
    area_type: str = ""  # e.g. "osd_manufacturing", "sterile_fill", "warehouse"


class Room(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str
    name: str
    room_class: str = ""  # e.g. "ISO_8", "Grade_D", "unclassified"
    gmp_critical: bool = False


class Equipment(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str
    equipment_id: str
    equipment_type: str  # e.g. "tablet_press", "ahu", "coating_pan", "blender"
    tag_prefix: str = ""  # PLC/BMS tag prefix for this asset
    description: str = ""
