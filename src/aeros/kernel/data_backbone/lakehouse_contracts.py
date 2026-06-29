"""Lakehouse data backbone contracts for the AWS-native assurance architecture."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LakehouseZone(str, Enum):
    BRONZE = 'bronze'
    SILVER = 'silver'
    GOLD = 'gold'
    AUDIT = 'audit'


class LakehouseColumn(BaseModel):
    name: str
    data_type: str
    nullable: bool = True
    description: str


class PartitionSpec(BaseModel):
    partition_keys: list[str] = Field(default_factory=list)
    partition_format: str


class RetentionPolicy(BaseModel):
    hot_days: int
    warm_days: int
    cold_days: int
    archive_days: int


class LakehouseTableContract(BaseModel):
    zone: LakehouseZone
    table_name: str
    description: str
    columns: list[LakehouseColumn] = Field(default_factory=list)
    partition_spec: PartitionSpec
    retention_policy: RetentionPolicy
    schema_version: str
    owner: str


class DataProductContract(BaseModel):
    product_id: str
    product_name: str
    zone: LakehouseZone
    source_tables: list[str] = Field(default_factory=list)
    output_tables: list[str] = Field(default_factory=list)
    description: str
    schema_version: str


_DEFAULT_RETENTION = RetentionPolicy(hot_days=30, warm_days=180, cold_days=365, archive_days=2555)
_AUDIT_RETENTION = RetentionPolicy(hot_days=90, warm_days=365, cold_days=2555, archive_days=3650)
_PARTITION = PartitionSpec(partition_keys=['tenant_id', 'site_id', 'date'], partition_format='date=YYYY-MM-DD')


def _column(name: str, data_type: str, description: str, nullable: bool = True) -> LakehouseColumn:
    return LakehouseColumn(name=name, data_type=data_type, nullable=nullable, description=description)


BRONZE_RAW_IOT_EVENTS = LakehouseTableContract(
    zone=LakehouseZone.BRONZE,
    table_name='raw_iot_events',
    description='Immutable raw industrial events from IoT Core, Greengrass V2, or SiteWise-adjacent ingestion.',
    columns=[
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('source_system', 'string', 'Originating system or connector.', False),
        _column('event_id', 'string', 'Source event identifier.', False),
        _column('event_timestamp', 'timestamp', 'Source event timestamp.', False),
        _column('payload', 'json', 'Raw source payload.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='industrial_ingestion',
)

BRONZE_RAW_SOURCE_RECORDS = LakehouseTableContract(
    zone=LakehouseZone.BRONZE,
    table_name='raw_source_records',
    description='Immutable raw records from MES, QMS, ERP, LIMS, CMMS, historians, and enterprise sources.',
    columns=[
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('source_system', 'string', 'Originating source system.', False),
        _column('record_id', 'string', 'Native source record ID.', False),
        _column('record_type', 'string', 'Source business object type.', False),
        _column('payload', 'json', 'Raw payload for audit replay.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='enterprise_ingestion',
)

SILVER_CANONICAL_EVENTS = LakehouseTableContract(
    zone=LakehouseZone.SILVER,
    table_name='canonical_events',
    description='Canonical operational events normalized across ingestion channels.',
    columns=[
        _column('event_id', 'string', 'Canonical event ID.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('fingerprint', 'string', 'Deterministic idempotency fingerprint.', False),
        _column('parameter', 'string', 'Observed parameter or metric.', False),
        _column('value', 'string', 'Stable serialized value.', False),
        _column('unit', 'string', 'Observed engineering unit.', True),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='canonicalization',
)

SILVER_CANONICAL_ASSETS = LakehouseTableContract(
    zone=LakehouseZone.SILVER,
    table_name='canonical_assets',
    description='Normalized equipment, utility, and asset hierarchy context aligned with SiteWise and enterprise references.',
    columns=[
        _column('asset_id', 'string', 'Canonical asset ID.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('asset_type', 'string', 'Equipment or utility class.', False),
        _column('area_id', 'string', 'Associated area identifier.'),
        _column('attributes', 'json', 'Extended asset attributes.'),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='asset_mastering',
)

SILVER_CANONICAL_BATCHES = LakehouseTableContract(
    zone=LakehouseZone.SILVER,
    table_name='canonical_batches',
    description='Normalized batch, product, and material context derived from MES/eBR and ERP.',
    columns=[
        _column('batch_id', 'string', 'Canonical batch ID.', False),
        _column('product_id', 'string', 'Canonical product ID.'),
        _column('material_lot_id', 'string', 'Canonical material lot ID.'),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('status', 'string', 'Operational batch status.'),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='operations_context',
)

SILVER_CANONICAL_QUALITY_RECORDS = LakehouseTableContract(
    zone=LakehouseZone.SILVER,
    table_name='canonical_quality_records',
    description='Normalized deviations, CAPAs, lab results, and quality signals from QMS/LIMS.',
    columns=[
        _column('record_id', 'string', 'Canonical quality record ID.', False),
        _column('record_type', 'string', 'Deviation, CAPA, lab result, or related type.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('status', 'string', 'Lifecycle state of the record.'),
        _column('payload', 'json', 'Normalized quality payload.'),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='quality_context',
)

SILVER_CANONICAL_MAINTENANCE_RECORDS = LakehouseTableContract(
    zone=LakehouseZone.SILVER,
    table_name='canonical_maintenance_records',
    description='Normalized maintenance and work-order records for recurrence and engineering context.',
    columns=[
        _column('work_order_id', 'string', 'Maintenance record identifier.', False),
        _column('asset_id', 'string', 'Related asset ID.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('completed_at', 'timestamp', 'Completion time.'),
        _column('summary', 'string', 'Maintenance summary text.'),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='maintenance_context',
)

GOLD_STATE_OF_CONTROL_ASSESSMENTS = LakehouseTableContract(
    zone=LakehouseZone.GOLD,
    table_name='state_of_control_assessments',
    description='Deterministic state-of-control decisions and supporting metrics.',
    columns=[
        _column('assessment_id', 'string', 'Assessment identifier.', False),
        _column('event_id', 'string', 'Related event ID.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('outcome', 'string', 'Deterministic outcome value.', False),
        _column('confidence', 'float', 'Confidence score from deterministic logic.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='assurance_engine',
)

GOLD_EVENT_TO_IMPACT_ASSESSMENTS = LakehouseTableContract(
    zone=LakehouseZone.GOLD,
    table_name='event_to_impact_assessments',
    description='Deterministic mapping from events to affected batches, products, materials, and quality risks.',
    columns=[
        _column('event_id', 'string', 'Related event ID.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('impacted_batch_id', 'string', 'Impacted batch identifier.'),
        _column('impacted_product_id', 'string', 'Impacted product identifier.'),
        _column('missing_evidence', 'json', 'Missing evidence checklist entries.'),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='impact_engine',
)

GOLD_EVIDENCE_PACKAGES = LakehouseTableContract(
    zone=LakehouseZone.GOLD,
    table_name='evidence_packages',
    description='Structured audit-ready evidence package outputs assembled from deterministic sources.',
    columns=[
        _column('package_id', 'string', 'Evidence package identifier.', False),
        _column('event_id', 'string', 'Related event ID.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('completeness_score', 'float', 'Evidence completeness score.', False),
        _column('manifest_path', 'string', 'Manifest pointer or storage URI.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='evidence_packaging',
)

GOLD_APQR_SECTIONS = LakehouseTableContract(
    zone=LakehouseZone.GOLD,
    table_name='apqr_sections',
    description='Deterministic APQR/PQR section outputs for governed reporting workflows.',
    columns=[
        _column('section_id', 'string', 'APQR section identifier.', False),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('product_id', 'string', 'Product identifier.'),
        _column('section_title', 'string', 'Section title.', False),
        _column('content', 'json', 'Structured section content.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_DEFAULT_RETENTION,
    schema_version='1.0',
    owner='apqr_engine',
)

AUDIT_IDEMPOTENCY_RECORDS = LakehouseTableContract(
    zone=LakehouseZone.AUDIT,
    table_name='idempotency_records',
    description='Replay-safe processing registry and duplicate handling evidence.',
    columns=[
        _column('fingerprint', 'string', 'Deterministic fingerprint.', False),
        _column('output_reference', 'string', 'Produced output reference.', False),
        _column('processor_version', 'string', 'Processor version string.', False),
        _column('processed_at', 'timestamp', 'Processing time.', False),
        _column('reprocessing_count', 'int', 'Duplicate replay count.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_AUDIT_RETENTION,
    schema_version='1.0',
    owner='audit_controls',
)

AUDIT_PROCESSING_MANIFESTS = LakehouseTableContract(
    zone=LakehouseZone.AUDIT,
    table_name='processing_manifests',
    description='Versioned processing manifests linking input, output, and transformation context.',
    columns=[
        _column('manifest_id', 'string', 'Manifest identifier.', False),
        _column('event_id', 'string', 'Related event ID.'),
        _column('tenant_id', 'string', 'Tenant scope.', False),
        _column('site_id', 'string', 'Site scope.', False),
        _column('version_key', 'string', 'Composite processing version key.', False),
        _column('manifest', 'json', 'Manifest body.', False),
    ],
    partition_spec=_PARTITION,
    retention_policy=_AUDIT_RETENTION,
    schema_version='1.0',
    owner='audit_controls',
)

AUDIT_RULE_VERSIONS = LakehouseTableContract(
    zone=LakehouseZone.AUDIT,
    table_name='rule_versions',
    description='Registered deterministic rule, schema, and ontology version references.',
    columns=[
        _column('rule_id', 'string', 'Rule identifier.', False),
        _column('rule_category', 'string', 'Rule family/category.', False),
        _column('version', 'string', 'Rule version string.', False),
        _column('schema_version', 'string', 'Linked schema version.', False),
        _column('ontology_version', 'string', 'Linked ontology version.', False),
        _column('description', 'string', 'Human-readable description.'),
    ],
    partition_spec=_PARTITION,
    retention_policy=_AUDIT_RETENTION,
    schema_version='1.0',
    owner='audit_controls',
)

ALL_TABLE_CONTRACTS = [
    BRONZE_RAW_IOT_EVENTS,
    BRONZE_RAW_SOURCE_RECORDS,
    SILVER_CANONICAL_EVENTS,
    SILVER_CANONICAL_ASSETS,
    SILVER_CANONICAL_BATCHES,
    SILVER_CANONICAL_QUALITY_RECORDS,
    SILVER_CANONICAL_MAINTENANCE_RECORDS,
    GOLD_STATE_OF_CONTROL_ASSESSMENTS,
    GOLD_EVENT_TO_IMPACT_ASSESSMENTS,
    GOLD_EVIDENCE_PACKAGES,
    GOLD_APQR_SECTIONS,
    AUDIT_IDEMPOTENCY_RECORDS,
    AUDIT_PROCESSING_MANIFESTS,
    AUDIT_RULE_VERSIONS,
]
