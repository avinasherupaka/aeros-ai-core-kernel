from __future__ import annotations

import json
from uuid import uuid4

from aeros.kernel.bedrock.guardrails import check_guardrails
from aeros.kernel.bedrock.runtime_contracts import BedrockGroundingPolicy, BedrockResponseEnvelope, BedrockRuntimeMode


class BedrockRuntimeClient:
    """
    Thin runtime wrapper that enforces guardrails on Bedrock responses.
    """

    def __init__(self, *, model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0", guardrail_id: str = "", guardrail_version: str = ""):
        self.model_id = model_id
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version

    def render(self, *, deterministic_answer_id: str, prompt: str, mode: BedrockRuntimeMode = BedrockRuntimeMode.NARRATIVE_RENDERING) -> BedrockResponseEnvelope:
        text = self._invoke_bedrock(prompt)
        result = check_guardrails(text)
        if not result.passed:
            text = "Guardrail policy blocked unsafe response content. Human review required."
        return BedrockResponseEnvelope(
            response_id=f"bedrock::{uuid4()}",
            mode=mode,
            deterministic_answer_id=deterministic_answer_id,
            rendered_text=text,
            grounding_policy=BedrockGroundingPolicy(),
            citations=[deterministic_answer_id],
            human_approval_required=True,
            metadata={
                "model_id": self.model_id,
                "guardrail_id": self.guardrail_id,
                "guardrail_version": self.guardrail_version,
                "guardrail_passed": result.passed,
                "guardrail_violation_count": result.violation_count,
            },
        )

    def _invoke_bedrock(self, prompt: str) -> str:
        try:
            import boto3  # type: ignore
        except Exception:
            return prompt

        client = boto3.client("bedrock-runtime")
        body = {"inputText": prompt}
        invoke_kwargs = {
            "modelId": self.model_id,
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps(body),
        }
        if self.guardrail_id:
            invoke_kwargs["guardrailIdentifier"] = self.guardrail_id
        if self.guardrail_version:
            invoke_kwargs["guardrailVersion"] = self.guardrail_version
        response = client.invoke_model(**invoke_kwargs)
        payload = json.loads(response["body"].read().decode("utf-8"))
        if isinstance(payload, dict):
            for key in ("outputText", "completion", "generation"):
                if key in payload and payload[key]:
                    return str(payload[key])
        return prompt
