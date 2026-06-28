"""
Asset context model — lightweight reference used to anchor events, measurements,
and evidence items to the ISA-95 hierarchy without re-embedding the full hierarchy.
"""

from pydantic import BaseModel


class AssetContext(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str
    asset_id: str
    asset_type: str
    description: str = ""
    tag_prefix: str = ""
