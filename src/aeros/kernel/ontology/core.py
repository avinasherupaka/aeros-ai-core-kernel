from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


CORE_ONTOLOGY_TYPES = [
    "Tenant",
    "Site",
    "Area",
    "Room",
    "Line",
    "ProcessCell",
    "Equipment",
    "UtilitySystem",
    "Sensor",
    "MaterialLot",
    "Product",
    "Recipe",
    "Batch",
    "Operation",
    "Phase",
    "ProcessParameter",
    "EnvironmentalParameter",
    "Alarm",
    "Event",
    "Deviation",
    "CAPA",
    "ChangeControl",
    "MaintenanceWorkOrder",
    "CalibrationRecord",
    "CleaningRecord",
    "LabIPQCResult",
    "SOPClause",
    "Specification",
    "DMSDocument",
    "QualityRisk",
    "EvidenceItem",
    "HumanReview",
    "Approval",
    "Dossier",
]


class OntologyEntity(BaseModel):
    entity_type: str
    entity_id: str
    name: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class OntologyRelationship(BaseModel):
    source_id: str
    source_type: str
    relationship_type: str
    target_id: str
    target_type: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class OntologyContext(BaseModel):
    tenant_id: str
    site_id: str
    scenario_id: str | None = None
    entities: list[OntologyEntity] = Field(default_factory=list)
    relationships: list[OntologyRelationship] = Field(default_factory=list)
    active_batch_id: str | None = None
    active_product_id: str | None = None
    active_material_lot_id: str | None = None
    active_operation: str | None = None
    active_phase: str | None = None

    def entity_index(self) -> dict[str, OntologyEntity]:
        return {entity.entity_id: entity for entity in self.entities}

    def find_entities(self, entity_type: str) -> list[OntologyEntity]:
        return [entity for entity in self.entities if entity.entity_type == entity_type]
