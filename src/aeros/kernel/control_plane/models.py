from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, Field

TrafficLight = Literal["green", "yellow", "red", "unknown"]


class InfrastructureMaskingRule:
    """Rules for detecting infrastructure-specific identifiers in UI-safe payloads."""

    FORBIDDEN_PATTERNS: ClassVar[list[str]] = [
        "sitewise::",
        "arn:aws:",
        "iot-core::",
        "lambda::",
        "bedrock::",
        "s3://",
        "dynamodb::",
        "iot-greengrass::",
        "connector_id:",
    ]


class TokenTranslation(BaseModel):
    raw_token: str
    domain_label: str
    taxonomy_level: Literal["enterprise", "site", "area", "line", "cell", "asset", "connector", "system"]
    archetype: str | None = None


class SiteHealthCard(BaseModel):
    site_id: str
    site_label: str
    archetype: str
    overall_status: TrafficLight
    equipment_health: TrafficLight
    connector_health: TrafficLight
    data_freshness: TrafficLight
    evidence_completeness: TrafficLight
    audit_readiness: TrafficLight
    open_events: int
    critical_events: int
    business_summary: str
    recommended_action: str | None = None
    last_updated: datetime


class AreaHealthCard(BaseModel):
    area_id: str
    area_label: str
    site_label: str
    overall_status: TrafficLight
    line_count: int
    active_alerts: int
    business_summary: str


class AssetHealthCard(BaseModel):
    asset_id: str
    asset_label: str
    domain_path: str
    overall_status: TrafficLight
    equipment_health: TrafficLight
    last_event_type: str | None = None
    last_event_summary: str | None = None
    maintenance_due: bool = False
    batch_context: str | None = None


class ConnectorStatusCard(BaseModel):
    connector_label: str
    system_type: str
    status: TrafficLight
    last_ingestion_label: str
    latency_ms: int | None = None
    latency_status: TrafficLight
    polling_interval_s: int | None = None
    records_last_hour: int | None = None
    sla_breach: bool = False
    degradation_reason: str | None = None
    recommended_action: str | None = None
    internal_connector_id: str | None = Field(default=None, alias="_connector_id", exclude=True)
    aws_resource_arn: str | None = Field(default=None, alias="_aws_resource_arn", exclude=True)


class ReadinessScore(BaseModel):
    dimension: str
    status: TrafficLight
    score_pct: int | None = None
    reason_codes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    sla_status: str | None = None
    evidence_citations: list[str] = Field(default_factory=list)


class SiteReadinessRollup(BaseModel):
    site_label: str
    archetype: str
    overall_status: TrafficLight
    dimensions: list[ReadinessScore]
    plant_risk_summary: str
    qa_release_posture: str
    audit_readiness_posture: str
    open_capas: int
    overdue_reviews: int
    last_updated: datetime


class EnterpriseReadinessRollup(BaseModel):
    overall_status: TrafficLight
    total_sites: int
    red_sites: int
    yellow_sites: int
    green_sites: int
    sites: list[SiteReadinessRollup]
    enterprise_summary: str
    top_risks: list[str]
    last_updated: datetime


class TopologyNode(BaseModel):
    node_id: str
    node_label: str
    node_type: Literal["enterprise", "site", "area", "line", "cell", "asset", "system", "connector"]
    status: TrafficLight
    parent_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class DataFlowEdge(BaseModel):
    source_label: str
    target_label: str
    flow_type: Literal["telemetry", "quality", "maintenance", "batch", "evidence", "workflow"]
    status: TrafficLight
    latency_label: str | None = None
    data_rate_label: str | None = None
    last_data_label: str | None = None
    degradation_reason: str | None = None


class ManufacturingSiteTopology(BaseModel):
    site_label: str
    archetype: str
    nodes: list[TopologyNode]
    edges: list[DataFlowEdge]
    automation_pyramid: list[TopologyNode]
    last_updated: datetime


class PersonaWorkflowCard(BaseModel):
    persona: Literal["system_admin", "qa", "plant_ops", "engineering", "leadership"]
    persona_label: str
    primary_objective: str
    kpis: list[dict[str, str]]
    alerts: list[dict[str, str]]
    recommended_actions: list[dict[str, str]]
    workflow_state: dict[str, Any]


class DossierReadinessCard(BaseModel):
    batch_id: str | None = None
    batch_label: str
    product_label: str
    site_label: str
    dossier_status: TrafficLight
    completeness_pct: int
    missing_evidence: list[str]
    open_capas: int
    qa_review_status: str
    human_approval_required: bool
    release_recommendation: str
    evidence_citations: list[str]


class AssistantResponse(BaseModel):
    question: str
    persona: str | None = None
    summary: str
    response_markdown: str
    response_format: Literal["markdown", "table", "executive_summary", "guided_remediation"]
    deterministic_facts: list[str] = Field(default_factory=list)
    inferred_explanations: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    human_approval_required: bool = False
    gxp_decision_deferred: bool = False
    evidence_citations: list[str] = Field(default_factory=list)
    prohibited_content_check_passed: bool = True


class MCPToolSchema(BaseModel):
    tool_name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    requires_persona: bool = False
    admin_only: bool = False


class ControlPlaneSnapshot(BaseModel):
    snapshot_id: str
    mode: Literal["local_mock", "aws_production"]
    generated_at: datetime
    enterprise_readiness: EnterpriseReadinessRollup
    topology: list[ManufacturingSiteTopology]
    connectors: list[ConnectorStatusCard]
    persona_workflows: dict[str, PersonaWorkflowCard]
    mcp_tools: list[MCPToolSchema]


def validate_no_infra_leak(obj: dict) -> list[str]:
    """Return path-qualified violations for any forbidden infrastructure token found."""

    violations: list[str] = []

    def _walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                key_text = str(key)
                lower_key = key_text.lower()
                for pattern in InfrastructureMaskingRule.FORBIDDEN_PATTERNS:
                    if pattern in lower_key:
                        violations.append(f"{path}.{key_text}: forbidden pattern '{pattern}'")
                _walk(nested, f"{path}.{key_text}")
            return
        if isinstance(value, list):
            for index, nested in enumerate(value):
                _walk(nested, f"{path}[{index}]")
            return
        if isinstance(value, str):
            lower_value = value.lower()
            for pattern in InfrastructureMaskingRule.FORBIDDEN_PATTERNS:
                if pattern in lower_value:
                    violations.append(f"{path}: forbidden pattern '{pattern}' in '{value}'")

    _walk(obj, "$")
    return violations
