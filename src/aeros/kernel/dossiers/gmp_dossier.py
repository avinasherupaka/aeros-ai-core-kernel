from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from aeros.kernel.config.messages import COMPLIANCE_NOTE, PROOF_POSITIONING

from aeros.kernel.assurance.evidence_graph import EvidenceGraphSnapshot
from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.assurance.reliability_intelligence import ReliabilityInsight
from aeros.kernel.models.canonical import AssuranceEvent, StateOfControlAssessment


class GMPDossier(BaseModel):
    event_id: str
    tenant_id: str
    site_id: str
    markdown_path: str
    json_path: str
    sections: dict[str, Any] = Field(default_factory=dict)


def _default_root() -> Path:
    return Path(__file__).resolve().parents[4] / "artifacts" / "evidence"


def _safe_path_segment(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]", "_", value)


def _resolve_output_root(output_root: str | Path | None) -> Path:
    default_root = _default_root().resolve()
    if output_root is None:
        return default_root
    candidate = Path(output_root).resolve()
    allowed_roots = [default_root, Path("/tmp").resolve()]
    if any(candidate == allowed or allowed in candidate.parents for allowed in allowed_roots):
        return candidate
    raise ValueError("output_root must be within the default evidence directory or /tmp")


def build_gmp_dossier(
    *,
    event: AssuranceEvent,
    assessment: StateOfControlAssessment,
    impact_assessment: ImpactAssessment,
    evidence_graph: EvidenceGraphSnapshot,
    reliability_insight: ReliabilityInsight,
    output_root: str | Path | None = None,
) -> GMPDossier:
    root = _resolve_output_root(output_root)
    event_dir = root / _safe_path_segment(event.tenant_id) / _safe_path_segment(event.site_id) / "events" / _safe_path_segment(event.event_id)
    event_dir.mkdir(parents=True, exist_ok=True)
    sections = {
        "event_summary": {
            "message": PROOF_POSITIONING,
            "event_id": event.event_id,
            "metric": event.metric,
            "severity": event.severity,
            "value": event.value,
            "batch_id": event.batch_id,
            "product_id": event.product_id,
        },
        "source_lineage": assessment.source_lineage,
        "timeline": {
            "breach_start": assessment.breach_start.isoformat() if assessment.breach_start else None,
            "breach_end": assessment.breach_end.isoformat() if assessment.breach_end else None,
            "assessed_at": assessment.assessed_at.isoformat(),
        },
        "state_of_control_assessment": assessment.model_dump(mode="json"),
        "impact_map": impact_assessment.model_dump(mode="json"),
        "evidence_table": impact_assessment.required_evidence,
        "similar_recurrent_events": reliability_insight.model_dump(mode="json"),
        "maintenance_context": reliability_insight.maintenance_context,
        "missing_evidence": impact_assessment.missing_evidence,
        "human_review_and_approval_placeholder": {
            "review": "QA/operations/engineering review required before quality decision.",
            "approval": "Human-approved, audit-ready evidence pack placeholder.",
        },
        "compliance_validation_note": COMPLIANCE_NOTE,
        "evidence_graph": evidence_graph.model_dump(mode="json"),
    }
    markdown_path = event_dir / "dossier.md"
    json_path = event_dir / "dossier.json"
    markdown = f"""# GMP Evidence Dossier — {event.event_id}

## 1. Event summary
- Utility event → area → batch/product/material → quality risk → evidence → decision.
- Event: {event.metric} / {event.event_type.value}
- Severity: {event.severity}
- Batch: {event.batch_id or 'n/a'}
- Product: {event.product_id or 'n/a'}

## 2. Source lineage
```json
{json.dumps(assessment.source_lineage, indent=2)}
```

## 3. Timeline
- Breach start: {sections['timeline']['breach_start']}
- Breach end: {sections['timeline']['breach_end']}
- Assessed at: {sections['timeline']['assessed_at']}

## 4. State-of-control assessment
- Outcome: {assessment.outcome.value}
- Severity: {assessment.severity}
- Confidence: {assessment.confidence}

## 5. Impact map
- Site: {impact_assessment.impacted_site}
- Area: {impact_assessment.impacted_area}
- Room: {impact_assessment.impacted_room}
- Batch: {impact_assessment.impacted_batch_id or 'n/a'}
- Product: {impact_assessment.impacted_product_id or 'n/a'}

## 6. Evidence table
{chr(10).join(f'- {item}' for item in impact_assessment.required_evidence)}

## 7. Similar/recurrent events
- Classification: {reliability_insight.classification.value}
- Prior similar events: {reliability_insight.recurrence_count}

## 8. Maintenance context
- {reliability_insight.maintenance_context or 'No recent maintenance context linked.'}

## 9. Missing evidence
{chr(10).join(f'- {item}' for item in impact_assessment.missing_evidence) if impact_assessment.missing_evidence else '- None'}

## 10. Human review and approval placeholder
- Human-approved, audit-ready evidence pack.
- Read-only-first for OT/GxP safety.

## 11. Compliance/validation note
{sections['compliance_validation_note']}
"""
    markdown_path.write_text(markdown)
    json_path.write_text(json.dumps(sections, indent=2))
    return GMPDossier(
        event_id=event.event_id,
        tenant_id=event.tenant_id,
        site_id=event.site_id,
        markdown_path=str(markdown_path),
        json_path=str(json_path),
        sections=sections,
    )

