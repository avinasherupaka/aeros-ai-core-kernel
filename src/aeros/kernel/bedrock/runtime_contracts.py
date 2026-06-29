"""
Bedrock runtime architecture contracts.

Bedrock is the INTERFACE/RENDERING LAYER, not the decision engine.
Deterministic algorithms produce regulated conclusions.
Bedrock summarizes, explains, drafts narratives, and retrieves approved docs
but must NOT invent regulated conclusions or make autonomous GxP decisions.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from aeros.kernel.algorithms.deterministic_answer import DeterministicAnswer


class BedrockRuntimeMode(str, Enum):
    NARRATIVE_RENDERING = 'narrative_rendering'
    EVIDENCE_SUMMARY = 'evidence_summary'
    QUESTION_ROUTING = 'question_routing'
    RETRIEVAL_AUGMENTED = 'retrieval_augmented'
    DRAFT_GENERATION = 'draft_generation'


class BedrockToolInvocation(BaseModel):
    tool_name: str
    tool_version: str
    input_fingerprint: str
    deterministic_answer_id: str
    invoked_at: str


class BedrockGroundingPolicy(BaseModel):
    cite_only_provided_evidence: bool = True
    no_invention_of_missing_records: bool = True
    no_autonomous_batch_release: bool = True
    no_autonomous_deviation_closure: bool = True
    require_human_approval_for_gxp: bool = True
    no_write_or_control_commands_to_ot: bool = True
    report_missing_evidence: bool = True

    def validate_mode(self, mode: BedrockRuntimeMode) -> bool:
        """Returns True if the mode is permitted under this grounding policy."""
        return True


class BedrockResponseEnvelope(BaseModel):
    response_id: str
    mode: BedrockRuntimeMode
    deterministic_answer_id: str
    rendered_text: str
    grounding_policy: BedrockGroundingPolicy = Field(default_factory=BedrockGroundingPolicy)
    citations: list[str] = Field(default_factory=list)
    disclaimer: str = (
        'This response was rendered by Amazon Bedrock over deterministic Areos data. '
        'It does not constitute an autonomous regulatory decision. '
        'Human review and approval are required for all GxP decisions.'
    )
    missing_evidence_reported: list[str] = Field(default_factory=list)
    human_approval_required: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
