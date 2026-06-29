from aeros.kernel.agents import QAAgent


def test_qa_agent_answers_batch_impact_question():
    response = QAAgent().ask("Was Batch BATCH-OSD-2026-001 potentially impacted?")

    assert response["human_approval_required"] is True
    assert "potentially impacted" in response["answer"].lower()


def test_qa_agent_refuses_autonomous_deviation_closure():
    response = QAAgent().ask("Can I close this deviation?")

    assert response["human_approval_required"] is True
    assert "requires human qa approval" in response["answer"].lower()
