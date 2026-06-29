from aeros.kernel.bedrock.guardrails import check_guardrails


def test_clean_response_passes():
    text = 'The humidity excursion has been assessed. Batch B-2024-001 may be impacted. Human review is required before any decision.'
    result = check_guardrails(text)
    assert result.passed
    assert result.violation_count == 0


def test_autonomous_batch_release_fails():
    text = 'Based on the data, the batch is released and no further review is needed.'
    result = check_guardrails(text)
    assert not result.passed
    assert result.violation_count >= 1


def test_autonomous_deviation_closure_fails():
    text = 'The system closes the deviation automatically based on the evidence.'
    result = check_guardrails(text)
    assert not result.passed


def test_ot_write_command_fails():
    text = 'Please write to PLC to reset the alarm condition.'
    result = check_guardrails(text)
    assert not result.passed


def test_automatic_compliance_claim_fails():
    text = 'The system is automatically 21 CFR Part 11 compliant and requires no validation.'
    result = check_guardrails(text)
    assert not result.passed


def test_multiple_violations_detected():
    text = (
        'The batch is released. Also, write to PLC to disable alarm. '
        'The system is automatically compliant.'
    )
    result = check_guardrails(text)
    assert not result.passed
    assert result.violation_count >= 2
