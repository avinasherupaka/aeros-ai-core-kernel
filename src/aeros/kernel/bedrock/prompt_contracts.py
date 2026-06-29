"""
Prompt template contracts for Bedrock.

These contracts constrain Bedrock to:
- cite only provided evidence
- not invent missing records
- not make batch release/closure decisions
- report missing evidence
- require human approval for GxP decisions
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PromptPersona(str, Enum):
    QA_REVIEWER = 'qa_reviewer'
    ENGINEERING = 'engineering'
    PLANT_HEAD = 'plant_head'
    VALIDATION_AUDIT = 'validation_audit'
    IT_OT = 'it_ot'


SYSTEM_PROMPT_CONSTRAINTS = """
You are an assurance assistant for Areos, an AWS-native industrial assurance platform.

Rules you MUST follow:
1. Cite only evidence provided in the context. Do not invent or fabricate records, batch IDs, timestamps, or test results.
2. If evidence is missing, explicitly report it. Do not assume missing evidence is satisfactory.
3. Do not make autonomous decisions about batch release, product disposition, deviation closure, or CAPA closure.
4. Do not claim the system is automatically 21 CFR Part 11 compliant. Use: "designed to support 21 CFR Part 11 / GxP controls."
5. All GxP decisions require human review and approval. Always state this.
6. Do not suggest writing to or controlling OT systems (PLCs, SCADA, BMS).
7. Your role is to explain, summarize, and draft — not to decide or approve.
8. Always include the deterministic answer ID and citations in your response.
"""


@dataclass(frozen=True)
class PromptTemplate:
    persona: PromptPersona
    template_id: str
    system_prompt: str
    user_prompt_prefix: str
    required_context_fields: tuple[str, ...]


QA_IMPACT_PROMPT = PromptTemplate(
    persona=PromptPersona.QA_REVIEWER,
    template_id='qa_impact_v1',
    system_prompt=SYSTEM_PROMPT_CONSTRAINTS,
    user_prompt_prefix=(
        'Given the following deterministic QA impact assessment (answer_id: {answer_id}), '
        'provide a clear explanation suitable for a QA reviewer. '
        'Context: {context}'
    ),
    required_context_fields=('answer_id', 'context'),
)

AUDIT_READINESS_PROMPT = PromptTemplate(
    persona=PromptPersona.VALIDATION_AUDIT,
    template_id='audit_readiness_v1',
    system_prompt=SYSTEM_PROMPT_CONSTRAINTS,
    user_prompt_prefix=(
        'Given the following deterministic audit readiness assessment (answer_id: {answer_id}), '
        'explain the evidence package status for a validation/audit reviewer. '
        'Context: {context}'
    ),
    required_context_fields=('answer_id', 'context'),
)

ENGINEERING_RELIABILITY_PROMPT = PromptTemplate(
    persona=PromptPersona.ENGINEERING,
    template_id='engineering_reliability_v1',
    system_prompt=SYSTEM_PROMPT_CONSTRAINTS,
    user_prompt_prefix=(
        'Given the following deterministic reliability analysis (answer_id: {answer_id}), '
        'summarize the findings and recommended actions for an engineering reviewer. '
        'Context: {context}'
    ),
    required_context_fields=('answer_id', 'context'),
)

PROMPT_REGISTRY: dict[str, PromptTemplate] = {
    t.template_id: t
    for t in [QA_IMPACT_PROMPT, AUDIT_READINESS_PROMPT, ENGINEERING_RELIABILITY_PROMPT]
}
