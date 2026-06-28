# Core Areos Ontology

Phase 3 defines a universal regulated-operations ontology so Areos can connect events to validated state, product impact, and audit evidence across industries.

## Core supported entity classes

- Tenant, Site, Area, Room/Zone, Line/Process Cell
- Equipment, UtilitySystem, Sensor/Tag
- MaterialLot, Product, Recipe, Batch
- Operation, Phase, ProcessParameter, EnvironmentalParameter
- Alarm, Event, Deviation, CAPA, ChangeControl
- MaintenanceWorkOrder, CalibrationRecord, CleaningRecord, Lab/IPQCResult
- SOPClause, Specification, QualityRisk
- EvidenceItem, HumanReview, Approval, Dossier

## Design intent

- Preserve tenant/site isolation
- Support batch/product/material impact mapping
- Preserve read-only source lineage
- Support industry-pack configuration instead of single-use hard-coded logic
