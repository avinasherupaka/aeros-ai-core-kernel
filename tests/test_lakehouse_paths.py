from aeros.kernel.data_backbone.bronze_silver_gold import bronze_path, silver_path, gold_path, audit_path, s3_key


def test_bronze_path_includes_source_system():
    p = bronze_path('tenant_a', 'site_1', 'bms', 'raw_iot_events', '2024-01-15')
    assert 'tenant_a' in p
    assert 'site_1' in p
    assert 'bms' in p
    assert '2024-01-15' in p
    assert p.startswith('bronze/')


def test_silver_path_no_source_system():
    p = silver_path('tenant_a', 'site_1', 'canonical_events', '2024-01-15')
    assert 'tenant_a' in p
    assert '2024-01-15' in p
    assert p.startswith('silver/')


def test_gold_path():
    p = gold_path('tenant_a', 'site_1', 'evidence_packages', '2024-01-15')
    assert p.startswith('gold/')
    assert 'tenant_a' in p


def test_audit_path():
    p = audit_path('tenant_a', 'site_1', 'idempotency_records', '2024-01-15')
    assert p.startswith('audit/')
    assert 'tenant_a' in p


def test_paths_are_tenant_scoped():
    p1 = silver_path('tenant_a', 'site_1', 'canonical_events', '2024-01-15')
    p2 = silver_path('tenant_b', 'site_1', 'canonical_events', '2024-01-15')
    assert p1 != p2


def test_s3_key():
    k = s3_key('my-bucket', 'silver/tenant_a/site_1/canonical_events/date=2024-01-15/')
    assert k.startswith('s3://my-bucket/')
