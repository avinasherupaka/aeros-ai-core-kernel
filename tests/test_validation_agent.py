from aeros.kernel.agents import ValidationAgent


def test_validation_agent_reports_audit_readiness():
    response = ValidationAgent().ask("Is the evidence package audit-ready?")

    assert response["audit_ready_status"] in {"audit_ready", "not_audit_ready"}


def test_validation_agent_returns_compliance_notes():
    response = ValidationAgent().ask("What validation/compliance notes apply?")

    assert response["validation_notes"]
