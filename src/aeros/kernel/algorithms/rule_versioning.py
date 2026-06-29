"""
Rule/schema/code versioning for deterministic processing.
All deterministic outputs are explainable by rule+schema+code versions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RuleCategory(str, Enum):
    STATE_OF_CONTROL = "state_of_control"
    EVENT_TO_IMPACT = "event_to_impact"
    RELIABILITY = "reliability"
    EVIDENCE_PACKAGING = "evidence_packaging"
    APQR = "apqr"
    INGESTION_NORMALIZATION = "ingestion_normalization"


@dataclass(frozen=True)
class RuleVersion:
    rule_id: str
    rule_category: RuleCategory
    version: str
    description: str


@dataclass(frozen=True)
class ProcessingContextVersion:
    kernel_version: str
    schema_version: str
    ontology_version: str
    rules: tuple[RuleVersion, ...]

    def version_key(self) -> str:
        """Stable composite key for this processing context."""
        parts = [
            f"kernel:{self.kernel_version}",
            f"schema:{self.schema_version}",
            f"ontology:{self.ontology_version}",
        ] + [f"{r.rule_id}:{r.version}" for r in sorted(self.rules, key=lambda r: r.rule_id)]
        return "|".join(parts)


@dataclass
class VersionedRuleSet:
    context: ProcessingContextVersion
    active_rules: list[RuleVersion] = field(default_factory=list)

    def add_rule(self, rule: RuleVersion) -> None:
        self.active_rules.append(rule)

    def get_rules_for_category(self, category: RuleCategory) -> list[RuleVersion]:
        return [r for r in self.active_rules if r.rule_category == category]


DEFAULT_PROCESSING_CONTEXT = ProcessingContextVersion(
    kernel_version="0.3.0",
    schema_version="1.0",
    ontology_version="1.0",
    rules=(
        RuleVersion("soc_excursion_v1", RuleCategory.STATE_OF_CONTROL, "1.0", "Temperature/humidity excursion detection"),
        RuleVersion("eti_batch_impact_v1", RuleCategory.EVENT_TO_IMPACT, "1.0", "Batch/product impact mapping"),
        RuleVersion("rel_recurrence_v1", RuleCategory.RELIABILITY, "1.0", "Event recurrence classification"),
        RuleVersion("ep_gmp_package_v1", RuleCategory.EVIDENCE_PACKAGING, "1.0", "GMP evidence package assembly"),
        RuleVersion("apqr_section_v1", RuleCategory.APQR, "1.0", "APQR section assembly"),
        RuleVersion("norm_canonical_v1", RuleCategory.INGESTION_NORMALIZATION, "1.0", "Canonical event normalization"),
    ),
)
