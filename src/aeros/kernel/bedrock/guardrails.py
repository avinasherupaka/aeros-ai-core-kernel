"""
Local Bedrock guardrail checks.

These checks run on Bedrock output BEFORE it is presented to users.
They enforce Areos platform rules: no autonomous claims, no fabricated evidence,
no OT write commands, no automatic compliance claims.
"""
from __future__ import annotations

from dataclasses import dataclass

PROHIBITED_AUTONOMOUS_PHRASES = [
    'batch is released',
    'deviation is closed',
    'capa is complete',
    'automatically compliant',
    'automatically 21 cfr part 11',
    'no human review needed',
    'no human approval needed',
    'approved without review',
    'system approves',
    'system releases',
    'system closes',
]

PROHIBITED_OT_CONTROL_PHRASES = [
    'write to plc',
    'send command to',
    'control the valve',
    'set setpoint',
    'override interlock',
    'disable alarm',
    'write to scada',
    'write to bms',
    'write to dcs',
]

PROHIBITED_FABRICATION_MARKERS = [
    'i have assumed',
    'assuming the missing',
    'fabricated record',
    'invented batch',
    'synthetic result',
]


@dataclass
class GuardrailViolation:
    rule: str
    matched_phrase: str
    excerpt: str


@dataclass
class GuardrailResult:
    passed: bool
    violations: list[GuardrailViolation]

    @property
    def violation_count(self) -> int:
        return len(self.violations)


def check_guardrails(response_text: str) -> GuardrailResult:
    """
    Check Bedrock response text against all guardrails.
    Returns GuardrailResult with passed=True only if no violations found.
    """
    text_lower = response_text.lower()
    violations: list[GuardrailViolation] = []

    for phrase in PROHIBITED_AUTONOMOUS_PHRASES:
        if phrase in text_lower:
            idx = text_lower.find(phrase)
            excerpt = response_text[max(0, idx - 40) : idx + len(phrase) + 40]
            violations.append(GuardrailViolation(
                rule='no_autonomous_release_or_closure',
                matched_phrase=phrase,
                excerpt=excerpt,
            ))

    for phrase in PROHIBITED_OT_CONTROL_PHRASES:
        if phrase in text_lower:
            idx = text_lower.find(phrase)
            excerpt = response_text[max(0, idx - 40) : idx + len(phrase) + 40]
            violations.append(GuardrailViolation(
                rule='no_ot_write_or_control_commands',
                matched_phrase=phrase,
                excerpt=excerpt,
            ))

    for phrase in PROHIBITED_FABRICATION_MARKERS:
        if phrase in text_lower:
            idx = text_lower.find(phrase)
            excerpt = response_text[max(0, idx - 40) : idx + len(phrase) + 40]
            violations.append(GuardrailViolation(
                rule='no_evidence_fabrication',
                matched_phrase=phrase,
                excerpt=excerpt,
            ))

    return GuardrailResult(passed=len(violations) == 0, violations=violations)
