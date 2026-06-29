from aeros.kernel.algorithms.fingerprints import EventFingerprintInput, compute_event_fingerprint, FINGERPRINT_SCHEMA_VERSION

BASE_INPUT = dict(
    tenant_id='tenant_a',
    site_id='site_1',
    source_system='bms',
    source_record_id='rec_001',
    source_timestamp='2024-01-15T10:00:00Z',
    parameter='temperature',
    value='26.5',
    unit='degC',
    schema_version=FINGERPRINT_SCHEMA_VERSION,
)


def make_fp(**overrides):
    return EventFingerprintInput(**{**BASE_INPUT, **overrides})


def test_same_input_same_fingerprint():
    fp1 = compute_event_fingerprint(make_fp())
    fp2 = compute_event_fingerprint(make_fp())
    assert fp1 == fp2


def test_different_value_different_fingerprint():
    fp1 = compute_event_fingerprint(make_fp(value='26.5'))
    fp2 = compute_event_fingerprint(make_fp(value='30.0'))
    assert fp1 != fp2


def test_fingerprint_is_64_char_hex():
    fp = compute_event_fingerprint(make_fp())
    assert len(fp) == 64
    assert all(c in '0123456789abcdef' for c in fp)


def test_different_tenants_different_fingerprint():
    fp1 = compute_event_fingerprint(make_fp(tenant_id='tenant_a'))
    fp2 = compute_event_fingerprint(make_fp(tenant_id='tenant_b'))
    assert fp1 != fp2


def test_schema_version_affects_fingerprint():
    fp1 = compute_event_fingerprint(make_fp(schema_version='1.0'))
    fp2 = compute_event_fingerprint(make_fp(schema_version='2.0'))
    assert fp1 != fp2
