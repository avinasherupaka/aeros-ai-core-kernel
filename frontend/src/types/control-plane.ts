export type TrafficLight = "green" | "yellow" | "red" | "unknown";
export type TaxonomyLevel = "enterprise" | "site" | "area" | "line" | "cell" | "asset" | "connector" | "system";
export type PersonaType = "system_admin" | "qa" | "plant_ops" | "engineering" | "leadership";
export type FlowType = "telemetry" | "quality" | "maintenance" | "batch" | "evidence" | "workflow";
export type ResponseFormat = "markdown" | "table" | "executive_summary" | "guided_remediation";
export type NodeType = "enterprise" | "site" | "area" | "line" | "cell" | "asset" | "system" | "connector";
export type OperationMode = "local_mock" | "aws_production";

export interface TokenTranslation {
  raw_token: string;
  domain_label: string;
  taxonomy_level: TaxonomyLevel;
  archetype?: string | null;
}

export interface SiteHealthCard {
  site_id: string;
  site_label: string;
  archetype: string;
  overall_status: TrafficLight;
  equipment_health: TrafficLight;
  connector_health: TrafficLight;
  data_freshness: TrafficLight;
  evidence_completeness: TrafficLight;
  audit_readiness: TrafficLight;
  open_events: number;
  critical_events: number;
  business_summary: string;
  recommended_action?: string | null;
  last_updated: string;
}

export interface AreaHealthCard {
  area_id: string;
  area_label: string;
  site_label: string;
  overall_status: TrafficLight;
  line_count: number;
  active_alerts: number;
  business_summary: string;
}

export interface AssetHealthCard {
  asset_id: string;
  asset_label: string;
  domain_path: string;
  overall_status: TrafficLight;
  equipment_health: TrafficLight;
  last_event_type?: string | null;
  last_event_summary?: string | null;
  maintenance_due: boolean;
  batch_context?: string | null;
}

export interface ConnectorStatusCard {
  connector_label: string;
  system_type: string;
  status: TrafficLight;
  last_ingestion_label: string;
  latency_ms?: number | null;
  latency_status: TrafficLight;
  polling_interval_s?: number | null;
  records_last_hour?: number | null;
  sla_breach: boolean;
  degradation_reason?: string | null;
  recommended_action?: string | null;
}

export interface ReadinessScore {
  dimension: string;
  status: TrafficLight;
  score_pct?: number | null;
  reason_codes: string[];
  recommended_actions: string[];
  sla_status?: string | null;
  evidence_citations: string[];
}

export interface SiteReadinessRollup {
  site_label: string;
  archetype: string;
  overall_status: TrafficLight;
  dimensions: ReadinessScore[];
  plant_risk_summary: string;
  qa_release_posture: string;
  audit_readiness_posture: string;
  open_capas: number;
  overdue_reviews: number;
  last_updated: string;
}

export interface EnterpriseReadinessRollup {
  overall_status: TrafficLight;
  total_sites: number;
  red_sites: number;
  yellow_sites: number;
  green_sites: number;
  sites: SiteReadinessRollup[];
  enterprise_summary: string;
  top_risks: string[];
  last_updated: string;
}

export interface TopologyNode {
  node_id: string;
  node_label: string;
  node_type: NodeType;
  status: TrafficLight;
  parent_id?: string | null;
  metadata: Record<string, string>;
}

export interface DataFlowEdge {
  source_label: string;
  target_label: string;
  flow_type: FlowType;
  status: TrafficLight;
  latency_label?: string | null;
  data_rate_label?: string | null;
  last_data_label?: string | null;
  degradation_reason?: string | null;
}

export interface ManufacturingSiteTopology {
  site_label: string;
  archetype: string;
  nodes: TopologyNode[];
  edges: DataFlowEdge[];
  automation_pyramid: TopologyNode[];
  last_updated: string;
}

export interface KPI { label: string; value: string; status: TrafficLight; trend?: string }
export interface WorkflowAlert { severity: TrafficLight; summary: string; owner: string; dueLabel: string }
export interface WorkflowAction { action: string; priority: "critical" | "high" | "medium" | "low"; rationale: string }

export interface PersonaWorkflowCard {
  persona: PersonaType;
  persona_label: string;
  primary_objective: string;
  kpis: KPI[];
  alerts: WorkflowAlert[];
  recommended_actions: WorkflowAction[];
  workflow_state: Record<string, unknown>;
}

export interface DossierReadinessCard {
  batch_id?: string | null;
  batch_label: string;
  product_label: string;
  site_label: string;
  dossier_status: TrafficLight;
  completeness_pct: number;
  missing_evidence: string[];
  open_capas: number;
  qa_review_status: string;
  human_approval_required: boolean;
  release_recommendation: string;
  evidence_citations: string[];
}

export interface AssistantResponse {
  question: string;
  persona?: string | null;
  summary: string;
  response_markdown: string;
  response_format: ResponseFormat;
  deterministic_facts: string[];
  inferred_explanations: string[];
  recommended_actions: string[];
  human_approval_required: boolean;
  gxp_decision_deferred: boolean;
  evidence_citations: string[];
  prohibited_content_check_passed: boolean;
}

export interface MCPToolSchema {
  tool_name: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  requires_persona: boolean;
  admin_only: boolean;
}

export interface ControlPlaneSnapshot {
  snapshot_id: string;
  mode: OperationMode;
  generated_at: string;
  enterprise_readiness: EnterpriseReadinessRollup;
  topology: ManufacturingSiteTopology[];
  connectors: ConnectorStatusCard[];
  persona_workflows: Record<string, PersonaWorkflowCard>;
  mcp_tools: MCPToolSchema[];
}

export interface AssistantQueryRequest {
  question: string;
  persona?: PersonaType;
  event_id?: string;
}

export interface StatusBadgeProps { status: TrafficLight; label?: string }
export interface DrilldownTarget { type: NodeType; id: string; label: string }

// ---- Active Event Command Center ----
export type EventStatus = "red" | "yellow" | "green";

export interface EventSummary {
  event_id: string;
  title: string;
  parameter: string;
  severity: string;
  status: EventStatus;
  outcome: string;
  site_label: string;
  room_label?: string | null;
  asset_label: string;
  batch_label?: string | null;
  product_label?: string | null;
  phase_label?: string | null;
  duration_minutes?: number | null;
  peak_value?: number | null;
  unit?: string | null;
}

export interface EventContext {
  parameter: string;
  asset_label: string;
  room_label?: string | null;
  batch_label?: string | null;
  product_label?: string | null;
  phase_label?: string | null;
  duration_minutes?: number | null;
  peak_value?: number | null;
  unit?: string | null;
  alert_limit?: number | null;
  action_limit?: number | null;
}

export interface EventImpact {
  risk_level: string;
  gxp_impact: boolean;
  capa_required: boolean;
  confidence_score?: number | null;
  confidence_explanation?: string | null;
  quality_risks: string[];
}

export interface EvidenceGraphNode {
  node_id: string;
  node_type: string;
  label: string;
  attributes: Record<string, unknown>;
}

export interface EvidenceGraphEdge {
  source_id: string;
  target_id: string;
  edge_type: string;
}

export interface EvidenceGraph {
  nodes: EvidenceGraphNode[];
  edges: EvidenceGraphEdge[];
}

export interface SeriesPoint {
  t: number;
  value: number | null;
}

export interface RequiredAction {
  label: string;
  status: "done" | "pending" | "blocked";
}

export interface EventDossierSummary {
  completeness_pct: number;
  missing_evidence: string[];
  required_evidence: string[];
}

export interface CommandCenterEvent {
  summary: EventSummary;
  context: EventContext;
  impact: EventImpact;
  series: SeriesPoint[];
  evidence_graph: EvidenceGraph;
  dossier: EventDossierSummary;
  required_actions: RequiredAction[];
}
