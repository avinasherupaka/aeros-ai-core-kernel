from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from aeros.kernel.ontology.core import OntologyContext, OntologyEntity, OntologyRelationship


class ParameterScenarioConfig(BaseModel):
    unit: str
    validated_range: dict[str, float] | None = None
    alert_limit: dict[str, float] | None = None
    action_limit: dict[str, float] | None = None
    critical_limit: dict[str, float] | None = None


class DemoTrigger(BaseModel):
    parameter: str
    breach_value: float
    duration_minutes: int = 1
    quality: str = "GOOD"


class ScenarioDefinition(BaseModel):
    scenario_id: str
    name: str
    industry: str
    process_area: str
    description: str
    source_systems: list[str] = Field(default_factory=list)
    source_protocols: list[str] = Field(default_factory=list)
    affected_parameters: list[str] = Field(default_factory=list)
    sample_limits: dict[str, ParameterScenarioConfig] = Field(default_factory=dict)
    possible_impacted_entities: dict[str, list[str] | str] = Field(default_factory=dict)
    quality_risks: list[str] = Field(default_factory=list)
    safety_risks: list[str] = Field(default_factory=list)
    compliance_risks: list[str] = Field(default_factory=list)
    evidence_checklist: list[str] = Field(default_factory=list)
    suggested_personas: list[str] = Field(default_factory=list)
    likely_source_records: list[str] = Field(default_factory=list)
    demo_triggers: list[DemoTrigger] = Field(default_factory=list)
    default_context: dict[str, Any] = Field(default_factory=dict)


class IndustryPack(BaseModel):
    pack_id: str
    name: str
    description: str
    scenarios: list[ScenarioDefinition] = Field(default_factory=list)


def scenario_library_path() -> Path:
    return Path(__file__).resolve().parents[4] / "artifacts" / "scenarios" / "regulated_scenario_library.json"


def load_scenario_library() -> list[IndustryPack]:
    data = json.loads(scenario_library_path().read_text())
    return [IndustryPack.model_validate(item) for item in data["industry_packs"]]


def list_industry_packs() -> list[dict[str, Any]]:
    return [
        {
            "pack_id": pack.pack_id,
            "name": pack.name,
            "description": pack.description,
            "scenario_ids": [scenario.scenario_id for scenario in pack.scenarios],
        }
        for pack in load_scenario_library()
    ]


def get_scenario_definition(scenario_id: str) -> ScenarioDefinition:
    for pack in load_scenario_library():
        for scenario in pack.scenarios:
            if scenario.scenario_id == scenario_id:
                return scenario
    raise KeyError(f"Unknown scenario_id: {scenario_id}")


def build_demo_ontology_context(scenario_id: str) -> OntologyContext:
    scenario = get_scenario_definition(scenario_id)
    context = scenario.default_context
    tenant_id = context.get("tenant_id", "acme_assurance")
    site_id = context.get("site_id", "site_demo_01")
    area_id = context.get("area_id", scenario.process_area.lower().replace(" ", "_"))
    room_id = context.get("room_id", f"{area_id}_zone")
    equipment_id = context.get("equipment_id", f"{scenario.process_area.lower().replace(' ', '_')}_asset_01")
    utility_system_id = context.get("utility_system_id", f"utility_{scenario.affected_parameters[0]}")
    batch_id = context.get("batch_id")
    product_id = context.get("product_id")
    material_lot_id = context.get("material_lot_id")
    operation = context.get("operation")
    phase = context.get("phase")

    entities = [
        OntologyEntity(entity_type="Tenant", entity_id=tenant_id, name=tenant_id.replace("_", " ").title()),
        OntologyEntity(entity_type="Site", entity_id=site_id, name=site_id.replace("_", " ").title(), attributes={"industry": scenario.industry}),
        OntologyEntity(entity_type="Area", entity_id=area_id, name=scenario.process_area),
        OntologyEntity(entity_type="Room", entity_id=room_id, name=context.get("room_name", room_id.replace("_", " ").title())),
        OntologyEntity(entity_type="Equipment", entity_id=equipment_id, name=context.get("equipment_name", equipment_id.replace("_", " ").title())),
        OntologyEntity(entity_type="UtilitySystem", entity_id=utility_system_id, name=context.get("utility_name", utility_system_id.replace("_", " ").title())),
    ]
    relationships = [
        OntologyRelationship(source_id=site_id, source_type="Site", relationship_type="CONTAINS", target_id=area_id, target_type="Area"),
        OntologyRelationship(source_id=area_id, source_type="Area", relationship_type="CONTAINS", target_id=room_id, target_type="Room"),
        OntologyRelationship(source_id=room_id, source_type="Room", relationship_type="USES", target_id=utility_system_id, target_type="UtilitySystem"),
        OntologyRelationship(source_id=room_id, source_type="Room", relationship_type="HOUSES", target_id=equipment_id, target_type="Equipment"),
    ]

    if batch_id:
        entities.append(OntologyEntity(entity_type="Batch", entity_id=batch_id, name=batch_id))
        relationships.append(OntologyRelationship(source_id=room_id, source_type="Room", relationship_type="ACTIVE_DURING", target_id=batch_id, target_type="Batch"))
    if product_id:
        entities.append(OntologyEntity(entity_type="Product", entity_id=product_id, name=product_id))
        relationships.append(OntologyRelationship(source_id=batch_id or room_id, source_type="Batch" if batch_id else "Room", relationship_type="PRODUCES", target_id=product_id, target_type="Product"))
    if material_lot_id:
        entities.append(OntologyEntity(entity_type="MaterialLot", entity_id=material_lot_id, name=material_lot_id))
    if operation:
        entities.append(OntologyEntity(entity_type="Operation", entity_id=operation, name=operation.replace("_", " ").title()))
    if phase:
        entities.append(OntologyEntity(entity_type="Phase", entity_id=phase, name=phase.replace("_", " ").title()))

    for parameter in scenario.affected_parameters:
        entities.append(
            OntologyEntity(
                entity_type="EnvironmentalParameter" if "humidity" in parameter or "temperature" in parameter or "pressure" in parameter else "ProcessParameter",
                entity_id=parameter,
                name=parameter.replace("_", " ").title(),
            )
        )

    for risk in scenario.quality_risks:
        risk_id = risk.lower().replace(" ", "_")
        entities.append(OntologyEntity(entity_type="QualityRisk", entity_id=risk_id, name=risk))
        relationships.append(OntologyRelationship(source_id=equipment_id, source_type="Equipment", relationship_type="HAS_RISK", target_id=risk_id, target_type="QualityRisk"))

    if any("documentum" in source.lower() for source in scenario.source_systems):
        dms_id = f"dms::{scenario.scenario_id}"
        entities.append(
            OntologyEntity(
                entity_type="DMSDocument",
                entity_id=dms_id,
                name=f"Documentum evidence package for {scenario.name}",
                attributes={"system": "OpenText Documentum"},
            )
        )
        relationships.append(
            OntologyRelationship(
                source_id=dms_id,
                source_type="DMSDocument",
                relationship_type="EVIDENCES",
                target_id=equipment_id,
                target_type="Equipment",
            )
        )

    return OntologyContext(
        tenant_id=tenant_id,
        site_id=site_id,
        scenario_id=scenario_id,
        entities=entities,
        relationships=relationships,
        active_batch_id=batch_id,
        active_product_id=product_id,
        active_material_lot_id=material_lot_id,
        active_operation=operation,
        active_phase=phase,
    )
