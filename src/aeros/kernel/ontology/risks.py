from pydantic import BaseModel, Field


class EvidenceRequirement(BaseModel):
    evidence_type: str
    description: str
    required: bool = True


class RiskCategoryMap(BaseModel):
    risk_category: str
    impacted_entities: list[str] = Field(default_factory=list)
    default_evidence: list[EvidenceRequirement] = Field(default_factory=list)
