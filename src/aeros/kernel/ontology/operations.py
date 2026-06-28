from pydantic import BaseModel


class BatchReference(BaseModel):
    batch_id: str
    product_id: str
    recipe_id: str
    operation: str
    phase: str
    status: str = "active"


class EquipmentReference(BaseModel):
    equipment_id: str
    equipment_type: str
    area_id: str
    room_id: str | None = None
