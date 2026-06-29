from aeros.kernel.bedrock.runtime_contracts import (
    BedrockRuntimeMode, BedrockGroundingPolicy, BedrockResponseEnvelope,
)
from aeros.kernel.bedrock.prompt_contracts import PROMPT_REGISTRY, PromptPersona


def test_grounding_policy_defaults():
    policy = BedrockGroundingPolicy()
    assert policy.cite_only_provided_evidence is True
    assert policy.no_autonomous_batch_release is True
    assert policy.require_human_approval_for_gxp is True
    assert policy.no_write_or_control_commands_to_ot is True


def test_bedrock_response_envelope_has_disclaimer():
    envelope = BedrockResponseEnvelope(
        response_id='resp_001',
        mode=BedrockRuntimeMode.NARRATIVE_RENDERING,
        deterministic_answer_id='ans_001',
        rendered_text='The event was assessed.',
    )
    assert 'human review' in envelope.disclaimer.lower() or 'approval' in envelope.disclaimer.lower()
    assert envelope.human_approval_required is True


def test_runtime_modes_include_narrative_rendering():
    assert BedrockRuntimeMode.NARRATIVE_RENDERING in list(BedrockRuntimeMode)


def test_prompt_registry_has_qa_template():
    assert 'qa_impact_v1' in PROMPT_REGISTRY


def test_prompt_registry_templates_have_system_constraints():
    for template_id, template in PROMPT_REGISTRY.items():
        assert 'human' in template.system_prompt.lower(), f'Template {template_id} missing human approval constraint'
