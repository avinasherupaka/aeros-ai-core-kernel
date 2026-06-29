from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
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
    manifest_path: str = ""
    evidence_index_path: str = ""
    source_citations_path: str = ""
    missing_evidence_checklist_path: str = ""
    approval_placeholder_path: str = ""
    package_hashes_path: str = ""
    package_completeness_score: float = 0.0


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

    manifest_path = event_dir / "manifest.json"
    evidence_index_path = event_dir / "evidence_index.json"
    source_citations_path = event_dir / "source_citations.json"
    missing_evidence_checklist_path = event_dir / "missing_evidence_checklist.json"
    approval_placeholder_path = event_dir / "approval_placeholder.json"
    package_hashes_path = event_dir / "package_hashes.json"

    manifest = {
        "package_id": f"pkg::{event.event_id}",
        "event_id": event.event_id,
        "tenant_id": event.tenant_id,
        "site_id": event.site_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": [
            {"name": "dossier.md", "type": "evidence_narrative", "path": str(markdown_path)},
            {"name": "dossier.json", "type": "evidence_json", "path": str(json_path)},
            {"name": "manifest.json", "type": "package_manifest", "path": str(manifest_path)},
            {"name": "evidence_index.json", "type": "evidence_index", "path": str(evidence_index_path)},
            {"name": "source_citations.json", "type": "source_citations", "path": str(source_citations_path)},
            {"name": "missing_evidence_checklist.json", "type": "missing_evidence", "path": str(missing_evidence_checklist_path)},
            {"name": "approval_placeholder.json", "type": "approval", "path": str(approval_placeholder_path)},
            {"name": "package_hashes.json", "type": "integrity", "path": str(package_hashes_path)},
        ],
        "compliance_note": COMPLIANCE_NOTE,
    }

    evidence_index = {
        "event_id": event.event_id,
        "required_evidence": [
            {
                "item": item,
                "status": "present" if item not in impact_assessment.missing_evidence else "missing",
                "source_hint": f"Refer to {assessment.source_lineage.get('source_system', 'source_system')} for this evidence item.",
            }
            for item in impact_assessment.required_evidence
        ],
        "evidence_graph_node_count": len(evidence_graph.nodes),
        "evidence_graph_edge_count": len(evidence_graph.edges),
    }

    source_citations = {
        "event_id": event.event_id,
        "citations": [
            {
                "source_system": assessment.source_lineage.get("source_system", "unknown"),
                "source_protocol": assessment.source_lineage.get("source_protocol", "unknown"),
                "connector_id": assessment.source_lineage.get("connector_id", "unknown"),
                "trace_id": event.trace_id or f"trace::{event.event_id}",
                "source_record_reference": assessment.source_lineage.get("source_record_reference", f"{event.asset_id}:{event.metric}"),
                "tenant_id": event.tenant_id,
                "site_id": event.site_id,
                "asset_id": event.asset_id,
                "metric": event.metric,
                "quality": assessment.source_lineage.get("quality", "GOOD"),
            }
        ],
    }

    missing_evidence_checklist = {
        "event_id": event.event_id,
        "items": [
            {
                "item": item,
                "status": "missing",
                "action_required": f"Obtain or confirm '{item}' before QA disposition.",
                "assigned_to": impact_assessment.suggested_human_review_owners[0] if impact_assessment.suggested_human_review_owners else "QA",
            }
            for item in impact_assessment.missing_evidence
        ],
        "total_missing": len(impact_assessment.missing_evidence),
    }

    approval_placeholder = {
        "event_id": event.event_id,
        "status": "pending_human_approval",
        "review_required_by": impact_assessment.suggested_human_review_owners,
        "review_statement": "QA/operations/engineering review required before quality decision. AI assists evidence generation; humans approve quality decisions.",
        "approval_statement": "Human-approved, audit-ready evidence pack placeholder.",
        "electronic_signature_placeholder": {
            "reviewer_name": "",
            "reviewer_role": "",
            "review_date": "",
            "approval_name": "",
            "approval_role": "",
            "approval_date": "",
            "meaning": "I confirm the evidence in this package has been reviewed and approved.",
        },
        "compliance_note": COMPLIANCE_NOTE,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2))
    evidence_index_path.write_text(json.dumps(evidence_index, indent=2))
    source_citations_path.write_text(json.dumps(source_citations, indent=2))
    missing_evidence_checklist_path.write_text(json.dumps(missing_evidence_checklist, indent=2))
    approval_placeholder_path.write_text(json.dumps(approval_placeholder, indent=2))

    package_hashes = {
        "event_id": event.event_id,
        "algorithm": "sha256",
        "hashes": {
            "dossier.md": hashlib.sha256(markdown_path.read_bytes()).hexdigest(),
            "dossier.json": hashlib.sha256(json_path.read_bytes()).hexdigest(),
            "manifest.json": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "evidence_index.json": hashlib.sha256(evidence_index_path.read_bytes()).hexdigest(),
            "source_citations.json": hashlib.sha256(source_citations_path.read_bytes()).hexdigest(),
            "missing_evidence_checklist.json": hashlib.sha256(missing_evidence_checklist_path.read_bytes()).hexdigest(),
            "approval_placeholder.json": hashlib.sha256(approval_placeholder_path.read_bytes()).hexdigest(),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Hashes computed at package generation time for local integrity verification.",
    }
    package_hashes_path.write_text(json.dumps(package_hashes, indent=2))

    total_evidence = max(len(impact_assessment.required_evidence), 1)
    present_evidence = total_evidence - len(impact_assessment.missing_evidence)
    package_completeness_score = round(present_evidence / total_evidence, 2)

    return GMPDossier(
        event_id=event.event_id,
        tenant_id=event.tenant_id,
        site_id=event.site_id,
        markdown_path=str(markdown_path),
        json_path=str(json_path),
        sections=sections,
        manifest_path=str(manifest_path),
        evidence_index_path=str(evidence_index_path),
        source_citations_path=str(source_citations_path),
        missing_evidence_checklist_path=str(missing_evidence_checklist_path),
        approval_placeholder_path=str(approval_placeholder_path),
        package_hashes_path=str(package_hashes_path),
        package_completeness_score=package_completeness_score,
    )

