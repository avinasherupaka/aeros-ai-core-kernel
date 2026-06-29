from aeros.kernel.data_backbone.query_contracts import IncidentQuery, execute_stub_query, RiskLevel, QueryStatus


def test_incident_query_required_fields():
    q = IncidentQuery(tenant_id='tenant_a', site_id='site_1')
    assert q.tenant_id == 'tenant_a'
    assert q.limit == 100
    assert q.offset == 0


def test_incident_query_with_filters():
    q = IncidentQuery(
        tenant_id='tenant_a',
        site_id='site_1',
        risk_levels=[RiskLevel.HIGH, RiskLevel.CRITICAL],
        statuses=[QueryStatus.OPEN],
    )
    assert RiskLevel.HIGH in q.risk_levels


def test_stub_query_returns_result():
    q = IncidentQuery(tenant_id='tenant_a', site_id='site_1')
    result = execute_stub_query(q)
    assert result.query.tenant_id == 'tenant_a'
    assert result.total_count == 0
    assert isinstance(result.results, list)
    assert result.data_backbone_version == '1.0'


def test_stub_query_has_informative_note():
    q = IncidentQuery(tenant_id='tenant_a', site_id='site_1')
    result = execute_stub_query(q)
    assert len(result.note) > 0
