from pydantic import BaseModel


class UtilityReading(BaseModel):
    tenant_id: str
    site_id: str
    asset_id: str
    metric: str
    value: float
    unit: str
    timestamp: str
