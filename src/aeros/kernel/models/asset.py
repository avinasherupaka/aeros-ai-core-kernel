from pydantic import BaseModel


class AssetContext(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str
    asset_id: str
    asset_type: str
