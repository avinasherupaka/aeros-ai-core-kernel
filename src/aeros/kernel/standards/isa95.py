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


class Area(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    name: str


class Room(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str
    name: str


class Equipment(BaseModel):
    tenant_id: str
    site_id: str
    area_id: str
    room_id: str
    equipment_id: str
    equipment_type: str
