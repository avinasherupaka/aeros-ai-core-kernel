from aeros.kernel.algorithms.idempotency import IdempotencyRegistry


def test_first_record_not_duplicate():
    registry = IdempotencyRegistry()
    was_dup, record = registry.check_and_record('fp_abc', 'out_001', 'proc_v1')
    assert not was_dup
    assert record.fingerprint == 'fp_abc'
    assert record.reprocessing_count == 0


def test_second_record_is_duplicate():
    registry = IdempotencyRegistry()
    registry.check_and_record('fp_abc', 'out_001', 'proc_v1')
    was_dup, record = registry.check_and_record('fp_abc', 'out_001', 'proc_v1')
    assert was_dup
    assert record.reprocessing_count == 1


def test_third_reprocessing_increments_count():
    registry = IdempotencyRegistry()
    registry.check_and_record('fp_xyz', 'out_001', 'proc_v1')
    registry.check_and_record('fp_xyz', 'out_001', 'proc_v1')
    was_dup, record = registry.check_and_record('fp_xyz', 'out_001', 'proc_v1')
    assert was_dup
    assert record.reprocessing_count == 2


def test_is_duplicate_false_for_new():
    registry = IdempotencyRegistry()
    assert not registry.is_duplicate('fp_new')


def test_is_duplicate_true_after_record():
    registry = IdempotencyRegistry()
    registry.check_and_record('fp_rec', 'out_001', 'proc_v1')
    assert registry.is_duplicate('fp_rec')


def test_get_record_returns_none_for_unknown():
    registry = IdempotencyRegistry()
    assert registry.get_record('unknown') is None


def test_record_count():
    registry = IdempotencyRegistry()
    registry.check_and_record('fp_1', 'out_1', 'v1')
    registry.check_and_record('fp_2', 'out_2', 'v1')
    registry.check_and_record('fp_1', 'out_1', 'v1')
    assert registry.record_count() == 2
