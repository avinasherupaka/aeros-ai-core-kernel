from __future__ import annotations

from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.dossiers.gmp_dossier import GMPDossier


class ValidationAuditRoomView(BaseModel):
    site_id: str
    evidence_lineage_completeness: dict[str, float] = Field(default_factory=dict)
    approval_status: dict[str, str] = Field(default_factory=dict)
    missing_source_records: dict[str, list[str]] = Field(default_factory=dict)
    validation_notes: list[str] = Field(default_factory=list)
    release_deployment_evidence_references: list[str] = Field(default_factory=list)


def build_validation_audit_room(
    *,
    site_id: str,
    dossiers: list[GMPDossier],
    impacts: list[ImpactAssessment],
) -> ValidationAuditRoomView:
    impact_index = {impact.event_id: impact for impact in impacts}
    completeness = {}
    approvals = {}
    missing_records = {}
    for dossier in dossiers:
        impact = impact_index[dossier.event_id]
        total = max(len(impact.required_evidence), 1)
        completeness[dossier.event_id] = round((total - len(impact.missing_evidence)) / total, 2)
        approvals[dossier.event_id] = "pending_human_approval"
        missing_records[dossier.event_id] = impact.missing_evidence
    return ValidationAuditRoomView(
        site_id=site_id,
        evidence_lineage_completeness=completeness,
        approval_status=approvals,
        missing_source_records=missing_records,
        validation_notes=[
            "Designed to support 21 CFR Part 11 / GxP controls, validation evidence, auditability, electronic-record integrity, and customer CSV.",
            "AI assists evidence generation; humans approve quality decisions.",
        ],
        release_deployment_evidence_references=[
            "docs/architecture/enterprise_release_lifecycle.md",
            "docs/compliance/release_validation_evidence.md",
        ],
    )
