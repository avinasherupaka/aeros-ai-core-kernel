from aeros.kernel.ontology.core import CORE_ONTOLOGY_TYPES
from aeros.kernel.ontology.industry_packs import build_demo_ontology_context


def test_core_ontology_supports_required_entity_types():
    required = {
        "Tenant", "Site", "Area", "Room", "Equipment", "UtilitySystem", "Sensor", "MaterialLot",
        "Product", "Recipe", "Batch", "Operation", "Phase", "ProcessParameter", "EnvironmentalParameter",
        "Alarm", "Event", "Deviation", "CAPA", "ChangeControl", "MaintenanceWorkOrder", "CalibrationRecord",
        "CleaningRecord", "LabIPQCResult", "SOPClause", "Specification", "QualityRisk", "EvidenceItem",
        "HumanReview", "Approval", "Dossier",
    }
    assert required.issubset(set(CORE_ONTOLOGY_TYPES))


def test_demo_ontology_context_contains_batch_and_risk_links():
    context = build_demo_ontology_context("pharma_osd_humidity_excursion_compression")
    entity_types = {entity.entity_type for entity in context.entities}
    assert {"Tenant", "Site", "Area", "Room", "Equipment", "UtilitySystem", "Batch", "Product", "MaterialLot", "QualityRisk"}.issubset(entity_types)
    assert context.active_batch_id == "BATCH-OSD-2026-001"
    assert any(relationship.relationship_type == "HAS_RISK" for relationship in context.relationships)
