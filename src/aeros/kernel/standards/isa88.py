from pydantic import BaseModel


class Procedure(BaseModel):
    procedure_id: str
    name: str


class Operation(BaseModel):
    operation_id: str
    procedure_id: str
    name: str


class Phase(BaseModel):
    phase_id: str
    operation_id: str
    name: str


class BatchRecord(BaseModel):
    tenant_id: str
    site_id: str
    batch_id: str
    product_id: str
    procedure_id: str
    operation_id: str
    phase_id: str
    status: str
