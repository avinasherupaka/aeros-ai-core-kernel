from pydantic import BaseModel, Field


class DeviationTriageDraft(BaseModel):
    event_id: str
    title: str
    status: str = "new"
    assignee: str | None = None
    impact_summary: str = ""
    evidence_checklist: list[str] = Field(default_factory=list)
    human_review_required: bool = True
