from aeros.kernel.data_backbone.lakehouse_contracts import (
    LakehouseZone,
    LakehouseTableContract,
    ALL_TABLE_CONTRACTS,
    BRONZE_RAW_IOT_EVENTS,
    SILVER_CANONICAL_EVENTS,
    GOLD_EVIDENCE_PACKAGES,
    AUDIT_IDEMPOTENCY_RECORDS,
)


def test_all_table_contracts_defined():
    assert len(ALL_TABLE_CONTRACTS) >= 13


def test_table_contracts_have_correct_zones():
    bronze = [t for t in ALL_TABLE_CONTRACTS if t.zone == LakehouseZone.BRONZE]
    silver = [t for t in ALL_TABLE_CONTRACTS if t.zone == LakehouseZone.SILVER]
    gold = [t for t in ALL_TABLE_CONTRACTS if t.zone == LakehouseZone.GOLD]
    audit = [t for t in ALL_TABLE_CONTRACTS if t.zone == LakehouseZone.AUDIT]
    assert len(bronze) >= 2
    assert len(silver) >= 5
    assert len(gold) >= 4
    assert len(audit) >= 3


def test_bronze_raw_iot_events_contract():
    c = BRONZE_RAW_IOT_EVENTS
    assert c.zone == LakehouseZone.BRONZE
    assert len(c.columns) >= 4
    assert c.partition_spec is not None


def test_all_contracts_have_schema_version():
    for t in ALL_TABLE_CONTRACTS:
        assert t.schema_version, f'Table {t.table_name} missing schema_version'


def test_all_contracts_have_columns():
    for t in ALL_TABLE_CONTRACTS:
        assert t.columns, f'Table {t.table_name} has no columns'
