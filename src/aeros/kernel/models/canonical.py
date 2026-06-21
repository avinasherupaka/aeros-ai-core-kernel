from pydantic import BaseModel


class CanonicalEvent(BaseModel):
    tenant_id: str
    site_id: str
    event_type: str
    source_system: str
    payload: dict
