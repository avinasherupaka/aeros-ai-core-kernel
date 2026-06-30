from aeros.kernel.bedrock.runtime_client import BedrockRuntimeClient


def test_runtime_client_blocks_guardrail_violation(monkeypatch):
    client = BedrockRuntimeClient()
    monkeypatch.setattr(client, "_invoke_bedrock", lambda prompt: "System approves deviation is closed.")
    envelope = client.render(deterministic_answer_id="ans-1", prompt="render this")
    assert envelope.metadata["guardrail_passed"] is False
    assert "blocked unsafe response" in envelope.rendered_text.lower()


def test_runtime_client_passes_safe_text(monkeypatch):
    client = BedrockRuntimeClient()
    monkeypatch.setattr(client, "_invoke_bedrock", lambda prompt: "Evidence summary prepared for human review.")
    envelope = client.render(deterministic_answer_id="ans-2", prompt="render this")
    assert envelope.metadata["guardrail_passed"] is True
