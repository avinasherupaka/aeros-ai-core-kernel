from pydantic import BaseModel, Field


class QualityRisk(BaseModel):
    risk_id: str
    category: str
    title: str
    description: str
    severity: str = "medium"
    evidence_requirements: list[str] = Field(default_factory=list)


class SOPClauseReference(BaseModel):
    sop_id: str
    clause_id: str
    title: str
    description: str = ""


class HumanReviewStep(BaseModel):
    persona: str
    objective: str
    approval_required: bool = True
