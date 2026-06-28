"""
Evidence source and item models for Areos.

Evidence sources record where data came from (BMS, EMS, MES, CMMS …) so that
QA can verify provenance without accessing the source system directly.

Areos principle: "Read-only-first for OT/GxP safety."
All source readings are captured with read_only=True to signal that Areos
never writes back to operational systems.

AWS equivalent:
  Evidence stored in S3 evidence lake with metadata in DynamoDB/Neptune.
  Provenance tracked via CloudTrail / custom lineage graph.
"""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """A single piece of evidence referenced in an assessment or dossier."""
    tenant_id: str
    site_id: str
    evidence_type: str
    reference_id: str
    description: str


class EvidenceSourceType(str, Enum):
    BMS = "bms"
    EMS = "ems"
    MES = "mes"
    QMS = "qms"
    CMMS = "cmms"
    LIMS = "lims"
    SCADA = "scada"
    OPC_UA = "opc_ua"
    SIMULATED = "simulated"
    MQTT = "mqtt"


class EvidenceSource(BaseModel):
    """
    A single source data point with full provenance.
    Used to build the evidence dossier for a StateOfControlAssessment.
    """
    source_id: str
    tenant_id: str
    site_id: str
    source_type: EvidenceSourceType
    system_name: str
    asset_id: str
    metric: str
    value: float
    unit: str
    timestamp: datetime
    topic: str | None = None
    trace_id: str | None = None
    quality: str = "GOOD"
    read_only: bool = True  # OT safety: Areos never writes back to source systems
    lineage: dict = Field(default_factory=dict)

