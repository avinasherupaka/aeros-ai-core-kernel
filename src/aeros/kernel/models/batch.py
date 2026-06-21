from pydantic import BaseModel


class BatchContext(BaseModel):
    tenant_id: str
    site_id: str
    batch_id: str
    product_id: str
    operation: str
    phase: str
    status: str
