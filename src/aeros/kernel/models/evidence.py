from pydantic import BaseModel


class EvidenceItem(BaseModel):
    tenant_id: str
    site_id: str
    evidence_type: str
    reference_id: str
    description: str
