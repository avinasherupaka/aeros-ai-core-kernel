from aeros.kernel.algorithms.deterministic_answer import (
    AnswerCitation,
    DecisionState,
    AnswerType,
    compose_qa_impact_answer,
    compose_audit_readiness_answer,
    compose_engineering_reliability_answer,
)

VERSIONS = {'kernel': '0.3.0', 'schema': '1.0'}
CITATION = AnswerCitation(source_system='bms', record_id='rec_001', record_type='event', timestamp='2024-01-15T10:00:00Z')


def test_qa_impact_answer_reproducible():
    kwargs = dict(
        answer_id='ans_001',
        event_summary='temperature excursion in room A',
        impacted_batches=['B-2024-001'],
        quality_risks=['sterility risk', 'particulate risk'],
        evidence_status='pending review',
        missing_evidence=[],
        citations=[CITATION],
        versions=VERSIONS,
    )
    a1 = compose_qa_impact_answer(**kwargs)
    a2 = compose_qa_impact_answer(**kwargs)
    assert a1.answer_text == a2.answer_text
    assert a1.decision_state == a2.decision_state
    assert a1.answer_type == AnswerType.QA_IMPACT


def test_qa_impact_with_missing_evidence_is_pending():
    answer = compose_qa_impact_answer(
        answer_id='ans_002',
        event_summary='humidity excursion',
        impacted_batches=[],
        quality_risks=[],
        evidence_status='incomplete',
        missing_evidence=['lab_result', 'deviation_form'],
        citations=[],
        versions=VERSIONS,
    )
    assert answer.decision_state == DecisionState.PENDING_HUMAN_REVIEW
    assert not answer.is_complete()


def test_qa_impact_human_review_always_required():
    answer = compose_qa_impact_answer(
        answer_id='ans_003', event_summary='test', impacted_batches=[], quality_risks=[],
        evidence_status='ok', missing_evidence=[], citations=[], versions=VERSIONS,
    )
    assert answer.human_review_required is True
    assert answer.requires_human_approval()


def test_audit_readiness_complete():
    answer = compose_audit_readiness_answer(
        answer_id='ans_004', event_id='EVT-001',
        dossier_completeness_score=1.0, missing_evidence=[],
        citations=[CITATION], versions=VERSIONS,
    )
    assert '100%' in answer.answer_text
    assert answer.human_review_required is True


def test_engineering_reliability_answer():
    answer = compose_engineering_reliability_answer(
        answer_id='ans_005', asset_id='HVAC-01',
        recurrence_count=3, recurrence_classification='recurring_excursion',
        recommended_actions=['schedule PM', 'inspect filters'],
        citations=[CITATION], versions=VERSIONS,
    )
    assert 'HVAC-01' in answer.answer_text
    assert answer.answer_type == AnswerType.ENGINEERING_RELIABILITY
