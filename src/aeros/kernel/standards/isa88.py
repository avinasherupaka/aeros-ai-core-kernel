"""
ISA-88 Part 1 inspired batch/process model for Areos.

Hierarchy: BatchRecord → Procedure → Operation → Phase.

Maps utility anomalies to the active manufacturing operation so that
Areos can trace: utility event → room → batch → product → quality risk.
"""

from pydantic import BaseModel


class Procedure(BaseModel):
    procedure_id: str
    name: str
    product_id: str = ""


class Operation(BaseModel):
    operation_id: str
    procedure_id: str
    name: str
    sequence: int = 0


class Phase(BaseModel):
    phase_id: str
    operation_id: str
    name: str
    sequence: int = 0
    critical_parameters: list[str] = []  # CPPs monitored in this phase


class BatchRecord(BaseModel):
    tenant_id: str
    site_id: str
    batch_id: str
    product_id: str
    procedure_id: str
    operation_id: str
    phase_id: str
    status: str  # "active", "completed", "on_hold", "rejected"
    area_id: str = ""
    room_id: str = ""
    equipment_id: str = ""
