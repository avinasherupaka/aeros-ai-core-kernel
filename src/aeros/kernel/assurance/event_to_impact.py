from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from aeros.kernel.models.canonical import AssuranceEvent
from aeros.kernel.ontology.core import OntologyContext
from aeros.kernel.ontology.industry_packs import ScenarioDefinition

_RISK_SCORE_CRITICAL_KEYWORD = 0.7
_RISK_SCORE_HIGH_KEYWORD = 0.6
_RISK_SCORE_HIGH_SEVERITY_EVENT = 0.5
_RISK_SCORE_DEFAULT = 0.4


class ImpactRationale(BaseModel):
    entity_id: str
    entity_type: str
    rationale: str
    risk_level: str = "medium"


class ImpactPath(BaseModel):
    event_id: str
    path_steps: list[str] = Field(default_factory=list)
    description: str = ""


class EvidenceStatus(BaseModel):
    evidence_item: str
    status: str
    source_hint: str = ""


class ImpactAssessment(BaseModel):
    event_id: str
    tenant_id: str
    site_id: str
    scenario_id: str | None = None
    impacted_site: str
    impacted_area: str | None = None
    impacted_room: str | None = None
    impacted_batch_id: str | None = None
    impacted_product_id: str | None = None
    impacted_material_lot_id: str | None = None
    active_operation: str | None = None
    active_phase: str | None = None
    likely_quality_risks: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    suggested_human_review_owners: list[str] = Field(default_factory=list)
    confidence_score: float
    confidence_explanation: str
    impacted_entities: dict[str, Any] = Field(default_factory=dict)
    impact_rationale: list[ImpactRationale] = Field(default_factory=list)
    impact_path: ImpactPath | None = None
    risk_severity_scores: dict[str, float] = Field(default_factory=dict)
    decision_options: list[str] = Field(default_factory=list)
    evidence_status_list: list[EvidenceStatus] = Field(default_factory=list)


def evaluate_event_impact(
    event: AssuranceEvent,
    ontology_context: OntologyContext,
    scenario_definition: ScenarioDefinition,
    *,
    available_evidence: list[str] | None = None,
) -> ImpactAssessment:
    available = set(available_evidence or [])
    missing = [item for item in scenario_definition.evidence_checklist if item not in available]
    area = next((entity.entity_id for entity in ontology_context.find_entities("Area")), None)
    room = next((entity.entity_id for entity in ontology_context.find_entities("Room")), None)

    confidence = 0.7
    reasons = ["Scenario metadata matched the event to ontology context."]
    if event.batch_id or ontology_context.active_batch_id:
        confidence += 0.15
        reasons.append("Batch context is available.")
    if event.product_id or ontology_context.active_product_id:
        confidence += 0.1
        reasons.append("Product context is available.")
    if missing:
        confidence -= min(0.25, 0.05 * len(missing))
        reasons.append("Some required evidence is still missing.")
    else:
        reasons.append("Required evidence checklist is complete.")

    impacted_entities = {
        "areas": scenario_definition.possible_impacted_entities.get("areas", [area] if area else []),
        "batches": scenario_definition.possible_impacted_entities.get("batches", [event.batch_id] if event.batch_id else []),
        "products": scenario_definition.possible_impacted_entities.get("products", [event.product_id] if event.product_id else []),
        "materials": scenario_definition.possible_impacted_entities.get("materials", [event.material_lot_id] if event.material_lot_id else []),
        "equipment": [event.asset_id],
    }

    impact_rationale = []
    for area_id in impacted_entities.get("areas", []):
        impact_rationale.append(ImpactRationale(
            entity_id=area_id,
            entity_type="Area",
            rationale=f"{event.metric} event at {event.site_id} impacted area {area_id}.",
            risk_level="medium",
        ))
    for batch_id in impacted_entities.get("batches", []):
        impact_rationale.append(ImpactRationale(
            entity_id=batch_id,
            entity_type="Batch",
            rationale=f"Batch {batch_id} was active during the {event.metric} event.",
            risk_level="medium",
        ))
    for product_id in impacted_entities.get("products", []):
        impact_rationale.append(ImpactRationale(
            entity_id=product_id,
            entity_type="Product",
            rationale=f"Product {product_id} was active during the {event.metric} event.",
            risk_level="medium",
        ))

    path_steps = [
        "event",
        event.area_id or "area",
        event.asset_id,
        event.batch_id or "batch/product",
        "quality_risk",
        "evidence",
        "decision",
    ]
    impact_path = ImpactPath(
        event_id=event.event_id,
        path_steps=path_steps,
        description=f"Lineage from event {event.event_id} to quality decision.",
    )

    risk_severity_scores = {}
    for risk in scenario_definition.quality_risks:
        if "critical" in risk.lower():
            risk_severity_scores[risk] = _RISK_SCORE_CRITICAL_KEYWORD
        elif "high" in risk.lower():
            risk_severity_scores[risk] = _RISK_SCORE_HIGH_KEYWORD
        elif event.severity in ("critical", "high"):
            risk_severity_scores[risk] = _RISK_SCORE_HIGH_SEVERITY_EVENT
        else:
            risk_severity_scores[risk] = _RISK_SCORE_DEFAULT

    decision_options = []
    if missing:
        decision_options.append("Potential impact; QA review required before disposition.")
    if event.severity == "critical":
        decision_options.append("Batch hold recommended pending investigation.")
    decision_options.append("No product impact likely pending evidence.")

    evidence_status_list = []
    for item in scenario_definition.evidence_checklist:
        status = "present" if item in available else "missing"
        evidence_status_list.append(EvidenceStatus(
            evidence_item=item,
            status=status,
            source_hint=f"Check source systems for {item}.",
        ))

    return ImpactAssessment(
        event_id=event.event_id,
        tenant_id=event.tenant_id,
        site_id=event.site_id,
        scenario_id=scenario_definition.scenario_id,
        impacted_site=event.site_id,
        impacted_area=area or event.area_id,
        impacted_room=room or event.room_id,
        impacted_batch_id=event.batch_id or ontology_context.active_batch_id,
        impacted_product_id=event.product_id or ontology_context.active_product_id,
        impacted_material_lot_id=event.material_lot_id or ontology_context.active_material_lot_id,
        active_operation=event.operation or ontology_context.active_operation,
        active_phase=event.phase or ontology_context.active_phase,
        likely_quality_risks=scenario_definition.quality_risks,
        required_evidence=scenario_definition.evidence_checklist,
        missing_evidence=missing,
        suggested_human_review_owners=scenario_definition.suggested_personas,
        confidence_score=round(max(0.1, min(confidence, 0.99)), 2),
        confidence_explanation=" ".join(reasons),
        impacted_entities=impacted_entities,
        impact_rationale=impact_rationale,
        impact_path=impact_path,
        risk_severity_scores=risk_severity_scores,
        decision_options=decision_options,
        evidence_status_list=evidence_status_list,
    )
