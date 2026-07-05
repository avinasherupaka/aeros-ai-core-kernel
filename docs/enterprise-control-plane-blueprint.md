# Enterprise Control Plane Blueprint

**Document Purpose:** Connected Manufacturing Enterprise Control Plane for Areos / Aeros AI Core Kernel

**Context:** Prepared for the current Python/FastAPI backend and planned React/TypeScript frontend with AWS production and Docker Compose local mode.

**Primary repository anchors:** `src/aeros/kernel/api/main.py`, `src/aeros/kernel/control_plane/service.py`, `src/aeros/kernel/models/`, `src/aeros/kernel/connectors/`, `infra/terraform/modules/`, `docker-compose.yml`, and `tests/`.

**Positioning statement:** This blueprint converts the current prototype into an enterprise-grade, read-only-first manufacturing control plane that normalizes OT/IT context, exposes persona-specific workflows, and grounds an MCP assistant in domain-safe manufacturing views rather than raw infrastructure payloads.

## Table of Contents

- 1. [Executive Summary](#1-executive-summary)
- 2. [Diagnosis of Current Prototype Flaws](#2-diagnosis-of-current-prototype-flaws)
- 3. [Target Architecture Overview](#3-target-architecture-overview)
- 4. [Domain Abstraction Model](#4-domain-abstraction-model)
- 5. [Normalized Data Model](#5-normalized-data-model)
- 6. [Topology and Data-Flow Design](#6-topology-and-data-flow-design)
- 7. [Readiness and Health Scoring Engine](#7-readiness-and-health-scoring-engine)
- 8. [Persona Workflows](#8-persona-workflows)
- 9. [MCP Assistant Design](#9-mcp-assistant-design)
- 10. [Local Developer Mode](#10-local-developer-mode)
- 11. [AWS Production Architecture](#11-aws-production-architecture)
- 12. [IaC and Deployment Strategy](#12-iac-and-deployment-strategy)
- 13. [UI/UX Blueprint](#13-uiux-blueprint)
- 14. [API Contracts](#14-api-contracts)
- 15. [Security and Compliance Posture](#15-security-and-compliance-posture)
- 16. [Testing and Validation Plan](#16-testing-and-validation-plan)
- 17. [Phased Implementation Roadmap](#17-phased-implementation-roadmap)
- 18. [Acceptance Criteria](#18-acceptance-criteria)
- 19. [Concrete Next Engineering Tasks](#19-concrete-next-engineering-tasks)

## 1. Executive Summary

The Connected Manufacturing Enterprise Control Plane is the operating surface that sits above heterogeneous plant, quality, maintenance, and enterprise systems and turns fragmented machine-centric data into human-actionable manufacturing context. The control plane does **not** replace MES, QMS, historian, ERP, CMMS, LIMS, SCADA, PLC, or AWS industrial services. Instead, it creates a governed abstraction layer that allows plant, quality, engineering, and leadership personas to reason about manufacturing state in business-safe language.

- A Python/FastAPI API layer already exists in `src/aeros/kernel/api/main.py`.
- A control-plane snapshot service already exists in `src/aeros/kernel/control_plane/service.py`.
- Connector packs already exist for historian, QMS/MES, CMMS/ERP/LIMS, MQTT, and OPC-UA.
- Domain models already exist for assets, batches, evidence, and canonical events in `src/aeros/kernel/models/`.
- Terraform modules already exist for foundation, IoT Core, SiteWise, evidence lake, workflow runtime, Neptune, observability, and tenant/site/cell segmentation.
- A substantial Python test suite already exists in `tests/`.

The target operating model of the control plane is enterprise read-only observability plus workflow coordination. The key design outcome is that all personas see **business-safe, explainable, role-appropriate** information rather than raw integration payloads or infrastructure identifiers. This blueprint introduces a formal domain abstraction layer, a normalized topology and readiness model, a React/TypeScript frontend, an MCP-grounded assistant, a richer Docker Compose developer mode, and a clear AWS production architecture.

- The control plane is a **system of assurance and coordination**, not the system of record.
- All regulated decisions remain human-mediated.
- All assistant responses are grounded and bounded.
- All status outcomes are explainable via reason codes.
- All user-facing APIs are domain-safe and infrastructure-redacted.

## 2. Diagnosis of Current Prototype Flaws

The current prototype successfully demonstrates deterministic evidence processing and simple control-plane storytelling. It is not yet a scalable enterprise architecture. The main flaws are leaky abstractions, lack of role-based context, an unstructured chatbot, and static topology assumptions.

| Flaw family | Current manifestation | Why it matters | Blueprint correction |
| --- | --- | --- | --- |
| Leaky abstractions | Backend internals and connector/artifact concepts bleed into user-facing representations. | Frontend and assistant surfaces become brittle and unsafe. | Introduce strict translation and masking rules. |
| Lack of role-based context | Persona summaries are shallow and generic. | Each persona lacks targeted workflow/action surfaces. | Define persona-specific pages, KPIs, and workflow models. |
| Unstructured chatbot | Keyword branching returns generic markdown. | No tool contracts, citations, or safety boundaries exist. | Move to MCP tools and structured AssistantResponse. |
| Static topology | Hard-coded site/area assumptions and event-derived topology. | Plants and lines cannot scale or be administered cleanly. | Create explicit topology and data-flow models. |

### Leaky abstractions

- Current service logic mixes evidence-root details, connector replay semantics, and user-facing business views.
- The frontend should never know how local artifact folders or raw AWS services are organized.
- Domain-safe APIs must become the only frontend contract.

### Lack of role-based context

- A QA user and a Plant Head should not consume the same “generic highlights” object.
- Workflow items need owner, SLA, next action, and evidence context.
- Persona routing and data slices must become first-class architecture.

### Unstructured chatbot

- Keyword heuristics are acceptable for demos but unsafe for enterprise workflows.
- The assistant must call deterministic tools and cite its evidence sources.
- The assistant must never imply regulated approval authority.

### Static topology

- A topology must exist even when there are no active events.
- Site/area/line/cell/asset structure should come from a managed registry or templates.
- Topology health and data-flow health need separate representations.

## 3. Target Architecture Overview

```text
Edge / OT → IoT Core / Greengrass → SiteWise / Normalization → Backbone → Control Plane API → React UI + MCP Assistant
```

The target architecture is layered, domain-safe, explainable, and productionizable. It explicitly separates source-system acquisition from normalization, evidence persistence, workflow coordination, user experience, and assistant orchestration.

| Layer | Responsibility | Representative technology |
| --- | --- | --- |
| Edge/OT | Read source systems without write-back. | Historian, MES, QMS, ERP, CMMS, OPC-UA, MQTT, PLC/SCADA/BMS. |
| IoT Core / Greengrass | Site-edge connector runtime and secure ingestion. | AWS IoT Greengrass V2, AWS IoT Core, rules. |
| SiteWise / Normalization | Asset and telemetry projection plus canonical event transformation. | AWS IoT SiteWise, Python normalization services. |
| Backbone | Persist evidence, workflow state, and queryable context. | S3, Aurora PostgreSQL, optional graph/search stores. |
| Control Plane API | Expose domain-safe control-plane contracts. | Python, FastAPI, Pydantic. |
| React UI + MCP Assistant | Persona-centric user experience and bounded guidance. | React, TypeScript, MCP server, Bedrock in production. |

## 4. Domain Abstraction Model

The domain abstraction model prevents the control plane from becoming a raw system-integration dashboard. It translates tokens, hides infrastructure internals, and defines the semantic hierarchy users interact with.

| Raw token | Domain-safe label |
| --- | --- |
| `hyd_site_01` | Hyderabad Plant 1 |
| `blr_bio_01` | Bengaluru Biopharma Campus |
| `powder_mixer_03` | Powder Mixer 3 |
| `qms-veeva-vault-live` | QMS / Veeva Vault |
| `historian-ignition-live` | BMS / Ignition Historian |

| Semantic taxonomy | Description |
| --- | --- |
| Site | Manufacturing location or campus. |
| Area | Operational segment within a site. |
| Line | Production or utility line within an area. |
| Cell/Room | Contained production or support environment. |
| Asset | Specific equipment or system component. |
| Batch/Product | Manufacturing lot or product context. |
| Event | Normalized operational or quality event. |
| Evidence | Supporting record or document. |
| Disposition | Governed business decision or workflow state. |

### Infrastructure masking rules
- Map raw AWS identifiers to public domain identifiers before frontend exposure.
- Map raw topic names and historian tags to approved semantic labels.
- Return evidence handles or signed URLs, never raw storage keys.
- Keep raw connector credentials, endpoints, and secrets backend-only.

### What must never leak to frontend
- Raw AWS IoT SiteWise asset/property IDs.
- Raw S3 bucket names and object keys.
- Greengrass component IDs, certificates, and deployment internals.
- Historian tag paths, OPC-UA node IDs, and raw MQTT topic structures.
- Secrets, credentials, account IDs, IAM role names, subnet IDs, or security-group IDs.

## 5. Normalized Data Model

### ControlPlaneSnapshot

Top-level aggregate used for dashboard and assistant context.

| Field | Type |
| --- | --- |
| snapshot_id | string |
| generated_at | datetime |
| environment | enum |
| enterprise_status | traffic_light |
| sites | SiteHealthCard[] |
| connectors | ConnectorStatus[] |
| readiness | ReadinessScore[] |
| topology | TopologyNode[] |
| flows | DataFlowEdge[] |
| persona_workflows | PersonaWorkflow[] |

### SiteHealthCard

Global site posture summary.

| Field | Type |
| --- | --- |
| site_id | string |
| site_label | string |
| site_type | enum |
| status | traffic_light |
| risk_score | number |
| readiness_score | number |
| freshness_seconds | integer |
| open_events | integer |
| blocked_batches | integer |
| top_reason_codes | string[] |

### ConnectorStatus

Health view of an integration connector.

| Field | Type |
| --- | --- |
| connector_public_id | string |
| source_system_label | string |
| site_scope | string|null |
| status | traffic_light |
| records_last_hour | integer |
| freshness_seconds | integer |
| latency_ms_p95 | integer |
| error_rate_percent | number |
| reason_codes | string[] |
| last_success_at | datetime|null |

### ReadinessScore

Deterministic score dimension.

| Field | Type |
| --- | --- |
| dimension | string |
| label | string |
| status | traffic_light |
| score | number |
| weight | number |
| reason_codes | string[] |
| explanation | string |
| updated_at | datetime |

### PersonaWorkflow

Persona-specific workflow board or guidance object.

| Field | Type |
| --- | --- |
| persona | string |
| view_id | string |
| headline | string |
| kpis | object[] |
| sections | object[] |
| actions | object[] |
| dependencies | string[] |
| sla_state | string |

### AssistantResponse

Structured answer returned by the assistant.

| Field | Type |
| --- | --- |
| request_id | string |
| answer_markdown | string |
| summary | string |
| status | traffic_light|null |
| reason_codes | string[] |
| citations | object[] |
| missing_evidence | object[] |
| recommended_actions | object[] |
| human_approval_required | boolean |

### TopologyNode

Normalized topology or workflow graph node.

| Field | Type |
| --- | --- |
| node_id | string |
| node_type | string |
| label | string |
| parent_node_id | string|null |
| status | traffic_light |
| metadata | object |
| reason_codes | string[] |
| updated_at | datetime |

### DataFlowEdge

Directional movement or dependency edge.

| Field | Type |
| --- | --- |
| edge_id | string |
| source_node_id | string |
| target_node_id | string |
| flow_type | string |
| status | traffic_light |
| freshness_seconds | integer|null |
| latency_ms_p95 | integer|null |
| reason_codes | string[] |

## 6. Topology and Data-Flow Design

```text
PLC / SCADA → BMS → Historian → MES → LIMS → QMS → ERP → CMMS → IoT Gateway / Greengrass → IoT Core / Rules → SiteWise → Evidence Graph → Workflow Engine → Control Plane UI → MCP Assistant
```

The control plane needs both a structural topology model and a data-flow model. Structural topology tells the system what exists; data-flow topology tells the system whether the evidence path is healthy enough to trust.

| Status | Rule |
| --- | --- |
| Green | All mandatory contributors are healthy and within SLA. |
| Yellow | At least one warning condition exists, but hard-stop blockers are absent. |
| Red | A hard-stop, mandatory evidence gap, critical asset issue, or failed mandatory connector exists. |

### Example biopharma site topology
```text
Bengaluru Biopharma Campus
├── Upstream Area
│   ├── Line U1
│   │   ├── Cell / Suite A
│   │   │   ├── Bioreactor 1
│   │   │   ├── Bioreactor 2
│   │   │   └── WFI Loop A
├── Downstream Area
│   ├── Line D1
│   │   ├── Chromatography Skid 1
│   │   ├── UFDF Skid 1
│   │   └── Cold Room 1
└── Quality / Release Area
    ├── QC Lab
    └── QA Release Queue
```

### Example OSD/API site topology
```text
Hyderabad Plant 1
├── Dispensing Area
│   ├── Line D4
│   │   ├── Dispensing Booth 1
│   │   ├── Powder Mixer 3
│   │   └── Material Transfer Station
├── Compression Area
│   ├── Line C4
│   │   ├── Tablet Press 4
│   │   ├── Metal Detector 1
│   │   └── Vision Inspection Station
└── Packaging Area
    ├── Line P2
    │   ├── Blister Packager 2
    │   └── Cartoner 1
```

| Source | Mapped state |
| --- | --- |
| Local JSON artifacts | Populate canonical event, workflow, evidence, and readiness state in local Postgres. |
| AWS IoT Core / Greengrass | Populate connector freshness, heartbeat, and inbound data-flow states. |
| AWS IoT SiteWise | Populate asset hierarchy and industrial telemetry projections. |
| S3 evidence lake | Populate evidence manifests and dossier references. |
| Aurora workflow state | Populate workflow boards, approvals, and ownership. |

## 7. Readiness and Health Scoring Engine

| Dimension | Purpose | Typical inputs |
| --- | --- | --- |
| equipment_health | Mechanical or environmental health of assets and utilities. | Telemetry thresholds, alarms, maintenance state, downtime markers. |
| connector_health | Availability and integrity of data integrations. | Heartbeat freshness, schema validation, retry failures, error rate. |
| data_freshness | How recent critical data is compared to configured SLA. | Last event age, missed cadence, stale cache. |
| data_quality | Validity and trustworthiness of incoming records. | Quality flags, schema completeness, duplicate rate, null rates. |
| evidence_completeness | Presence of required supporting records and documents. | Expected-vs-present evidence manifest. |
| dossier_readiness | Completeness and reviewability of the batch/event dossier. | Dossier section completion, reviewer assignments, pending gaps. |
| qa_release_readiness | Whether QA can proceed to release review. | Evidence completeness, deviation holds, approval status. |
| capa_deviation_readiness | Ability to triage or close CAPA/deviation activities. | Investigation fields, root-cause links, action completion. |
| audit_readiness | Whether the state is suitable for audit review. | Traceability, signed approvals, document completeness. |
| plant_risk | Operational and quality risk posture of the site/line. | Critical events, chronic issues, blocked batches. |
| pipeline_health | Health of ingestion and processing backbone. | Queue lag, rule failures, processing latency. |
| site_posture | Overall site state from weighted dimensions. | Rollup across mandatory dimensions. |

### Hierarchical rollups
```text
asset → line → area → site → enterprise
```

### Explainability with reason codes
| Reason code | Meaning |
| --- | --- |
| CONNECTOR_STALE | No successful update within configured freshness window. |
| CONNECTOR_ERROR_BURST | Recent connector failures exceed error threshold. |
| SCHEMA_VALIDATION_FAILED | Source records do not meet canonical contract. |
| ASSET_HEALTH_WARNING | Asset telemetry indicates degraded but not failed state. |
| ASSET_HEALTH_CRITICAL | Asset telemetry indicates critical failure or breach. |
| MISSING_MANDATORY_EVIDENCE | Required evidence item absent for current context. |
| DOSSIER_SECTION_INCOMPLETE | One or more dossier sections incomplete or unreviewed. |
| QA_HOLD_ACTIVE | QA hold or deviation prevents release progress. |
| AUDIT_TRACE_GAP | Traceability chain incomplete or unverifiable. |
| PIPELINE_LATENCY_BREACH | Pipeline latency exceeds SLA. |
| NO_SILENT_FAILURE_ALLOWED | A subsystem failed without a visible status update; force red/alert. |
| ROLLUP_CHILD_RED | Parent status red because at least one mandated child is red. |

### SLA configuration
| SLA | Example | Breach outcome |
| --- | --- | --- |
| Freshness SLA | Historian feed every 60 seconds | Yellow at 120 seconds, red at 300 seconds |
| Action SLA | QA review within 4 business hours | Yellow near deadline, red at breach |
| Evidence SLA | Mandatory release evidence present before review | Yellow pending, red when release window is hit |

### No-silent-failures rule
Any failure to ingest, score, enrich, or publish state must surface as an explicit status. Missing cards or empty arrays are never a substitute for health indicators.

### Example status object
```json
{
  "dimension": "evidence_completeness",
  "label": "Evidence Completeness",
  "status": "yellow",
  "score": 76,
  "weight": 0.12,
  "reason_codes": ["MISSING_MANDATORY_EVIDENCE", "DOSSIER_SECTION_INCOMPLETE"],
  "explanation": "One QA review attachment is still missing.",
  "updated_at": "2026-06-01T10:14:32Z"
}
```

### Example rollup object
```json
{
  "subject_type": "site",
  "subject_id": "site-bio-blr-01",
  "subject_label": "Bengaluru Biopharma Campus",
  "status": "yellow",
  "score": 81,
  "reason_codes": ["ROLLUP_CHILD_RED", "CONNECTOR_STALE", "QA_HOLD_ACTIVE"],
  "updated_at": "2026-06-01T10:15:00Z"
}
```

## 8. Persona Workflows

### System Administrator

**Objective:** Maintain connector health, topology integrity, policy compliance, and platform diagnostics.

**Information architecture**
- Admin Diagnostics dashboard
- Connector Health table
- Topology Registry editor
- Environment Diff / Drift view
- Assistant audit log

**KPI definitions**
- Connectors green %
- Stale feeds count
- Topology translation misses
- API p95 latency
- Assistant tool success rate

**Workflow/action model**
1. Review red/yellow connectors
2. Investigate missing mappings or stale feeds
3. Acknowledge/assign incidents
4. Verify recovery and close diagnostic event

**Example UI sections**
- Global health banner
- Connector matrix
- Topology diff panel
- Policy warnings drawer
- Pipeline event timeline

**Data dependencies**
- Connector heartbeat telemetry
- CloudWatch metrics
- translation catalog
- topology registry
- workflow incident table

**API endpoints**
- GET /cp/connectors
- GET /cp/topology
- GET /cp/readiness?scope=platform
- POST /cp/assistant/query

### Quality Assurance

**Objective:** Assess evidence completeness, release readiness, deviation/CAPA impact, and audit traceability.

**Information architecture**
- QA Release Board
- Batch Tracker
- Dossier Viewer
- CAPA/Deviation Queue
- Evidence gap panel

**KPI definitions**
- Batches release-ready
- Batches blocked
- Mandatory evidence gaps
- Pending approvals
- Audit-ready %

**Workflow/action model**
1. Open release board
2. Inspect blocked batches
3. Review dossier completeness and evidence
4. Assign or request missing evidence
5. Approve or hold release

**Example UI sections**
- Release board columns
- Batch summary cards
- Dossier completeness progress
- Evidence citations panel
- Human approval footer

**Data dependencies**
- MES batch context
- QMS deviation records
- LIMS results
- evidence manifests
- workflow approvals

**API endpoints**
- GET /cp/readiness
- GET /cp/dossiers/{batch_id}
- GET /cp/capa/queue
- POST /cp/assistant/query

### Plant Head / Plant Ops

**Objective:** Monitor site posture, line readiness, operational bottlenecks, and business risk.

**Information architecture**
- Executive Dashboard
- Site Detail
- Line Detail
- Risk summary view
- Action tracker

**KPI definitions**
- Lines green/yellow/red
- Open high-risk events
- Blocked batches
- Downtime minutes
- Site risk tier

**Workflow/action model**
1. Scan dashboard
2. Drill into yellow/red lines
3. Review blockers and owners
4. Escalate cross-functional actions
5. Confirm recovery

**Example UI sections**
- Site cards
- Line readiness strip
- Ownership table
- Trend charts
- Escalation widget

**Data dependencies**
- Site rollups
- asset health
- batch readiness
- connector posture
- workflow ownership state

**API endpoints**
- GET /cp/sites
- GET /cp/sites/{site_id}/health
- GET /cp/topology
- GET /cp/readiness
- POST /cp/assistant/query

### Engineering / Reliability

**Objective:** Identify chronic equipment issues, telemetry anomalies, maintenance impacts, and recovery actions.

**Information architecture**
- Reliability Board
- Asset Detail
- Maintenance impact view
- Connector/asset correlation panel

**KPI definitions**
- Critical assets
- Repeat deviations
- Mean time to recovery
- Maintenance work orders open
- Telemetry quality issues

**Workflow/action model**
1. Review chronic assets
2. Correlate failures with maintenance and telemetry
3. Open investigation or maintenance action
4. Track resolution effectiveness

**Example UI sections**
- Asset risk heatmap
- Telemetry timeline
- Work-order linkage
- Root-cause hypothesis notes
- Recommended next checks

**Data dependencies**
- Historian data
- CMMS work orders
- connector health
- asset topology
- assurance events

**API endpoints**
- GET /cp/topology
- GET /cp/connectors
- GET /cp/readiness?scope=asset
- POST /cp/assistant/query

### Leadership

**Objective:** See enterprise posture, portfolio risk, site comparison, and readiness trends without operational noise.

**Information architecture**
- Enterprise Dashboard
- Site Comparison board
- Risk Trend view
- Strategic summary feed

**KPI definitions**
- Sites green/yellow/red
- Enterprise risk index
- Release throughput at risk
- Audit readiness trend
- Top systemic bottlenecks

**Workflow/action model**
1. Review enterprise summary
2. Compare site posture
3. Identify common bottlenecks
4. Trigger governance reviews or investments

**Example UI sections**
- Enterprise scorecards
- Comparison matrix
- Trend narratives
- Top risks list
- Strategic actions panel

**Data dependencies**
- Aggregated site rollups
- workflow trend history
- connector/site posture summaries
- business calendar context

**API endpoints**
- GET /cp/sites
- GET /cp/readiness?scope=enterprise
- GET /cp/personas/leadership/workflow
- POST /cp/assistant/query

## 9. MCP Assistant Design

The assistant is implemented behind an MCP server/tool boundary. It answers operational questions by invoking deterministic control-plane tools rather than by reading raw source payloads or improvising unsupported logic.

| Tool | Input schema | Output schema |
| --- | --- | --- |
| get_site_status | {site_id} | {site, readiness, top_reason_codes} |
| get_connector_health | {site_id?, connector_type?} | {connectors} |
| get_line_readiness | {site_id, line_id} | {line, dimensions, blockers} |
| get_dossier_status | {batch_id} | {batch_id, status, completeness, missing_evidence} |
| get_capa_history | {subject_id, subject_type} | {open_items, history} |
| get_batch_release_status | {batch_id} | {batch, release_status, blockers, approvals} |
| get_missing_evidence | {subject_id, subject_type} | {missing_evidence, severity} |
| get_plant_risk_summary | {site_id} | {risk_index, top_risks, recommended_actions} |
| get_workflow_guidance | {persona, subject_id?} | {workflow, guidance} |

### Assistant response schema
```json
{
  "request_id": "asst-2026-06-01-001",
  "summary": "Compression Line 4 is yellow because one connector is stale and one mandatory QA evidence item is pending.",
  "answer_markdown": "### Why Line 4 is yellow
...",
  "status": "yellow",
  "reason_codes": ["CONNECTOR_STALE", "MISSING_MANDATORY_EVIDENCE"],
  "citations": [],
  "missing_evidence": [],
  "recommended_actions": [],
  "human_approval_required": true
}
```

### Good response examples
- **Why is Line 4 yellow?** — Explain yellow contributors, list reason codes, and recommend role-appropriate actions.
- **Is BIO-BATCH-204 ready for release?** — State current release posture, blockers, approvals pending, and human-approval note.
- **What should QA do next?** — Prioritize highest-impact evidence or approval actions from the QA workflow board.

### Prohibited response examples
- Do not say a batch is approved or released without human approval.
- Do not leak raw AWS IDs or raw source-system tokens.
- Do not invent missing evidence or unknown states.
- Do not hide degraded or stale source conditions.

### Local context ingestion
- Use Postgres-backed read models populated by mock-ingestion-engine.
- Use deterministic artifact-derived workflow and evidence summaries.

### AWS production context sources
- Aurora workflow/readiness tables.
- SiteWise-derived topology and telemetry projections.
- S3 evidence manifests and dossier references.
- Assistant-safe graph/search summaries where approved.

## 10. Local Developer Mode

```text
Docker Compose Services
├── api
├── ui
├── postgres
├── mock-ingestion-engine
└── mcp-server
```

| Service | Responsibility |
| --- | --- |
| api | Expose `/cp/*` endpoints and assistant query API. |
| ui | Serve React/TypeScript application. |
| postgres | Store workflow + read-model state. |
| mock-ingestion-engine | Watch mock JSON folders and write normalized state. |
| mcp-server | Host local deterministic MCP tools. |

### Local DB schema
- `cp_topology_nodes`
- `cp_data_flow_edges`
- `cp_connector_status`
- `cp_readiness_scores`
- `cp_workflow_items`
- `cp_evidence_manifest`
- `cp_batches`
- `cp_assistant_audit`

### Startup command
```bash
docker compose up --build api ui postgres mock-ingestion-engine mcp-server
```

### Developer workflow
1. Start local services.
2. Seed or edit mock source files.
3. Observe normalization into Postgres.
4. Inspect dashboard/topology/persona pages.
5. Ask the assistant bounded questions.
6. Run tests for APIs, workflows, and leakage protections.

## 11. AWS Production Architecture

```text
CloudFront / S3 UI
        ↓
App Runner API
        ↓
Aurora PostgreSQL + S3 Evidence Lake + SiteWise
        ↑
IoT Core + Greengrass ingestion
        ↑
Plant and enterprise source systems

Bedrock + MCP assistant consume only approved read models and evidence summaries
```

### Key production components
- CloudFront/S3 for UI hosting.
- App Runner for Python/FastAPI API hosting.
- IoT Core + Greengrass + SiteWise for ingestion and industrial state.
- S3 evidence lake + Aurora workflow state + SiteWise time-series.
- Bedrock + MCP assistant with policy boundaries.
- Least-privilege IAM and CloudWatch observability.

### Failure modes and resilience
| Failure mode | Resilience response |
| --- | --- |
| Connector outage | Mark connector red, degrade dependent state, alert operators. |
| IoT routing failure | Alarm, retry, surface pipeline red state. |
| SiteWise lag | Mark freshness degraded and propagate to dependent rollups. |
| Aurora issue | Use resilience patterns and raise platform incidents; keep stale-state timestamps visible. |
| Assistant issue | Degrade assistant only; keep core workflows operating. |

## 12. IaC and Deployment Strategy

Terraform is the preferred IaC approach for this blueprint because the repository already contains Terraform modules and the declarative workflow is appropriate for reviewed, auditable enterprise infrastructure changes.

| Module | Purpose |
| --- | --- |
| control_plane_api | App Runner service, config, networking, alarms. |
| ui_hosting | S3, CloudFront, DNS, TLS. |
| iot_ingestion | IoT Core, Greengrass, routing, ingest policies. |
| workflow_storage | Aurora and related workflow data infrastructure. |
| mcp_assistant | Bedrock, MCP runtime, audit logging. |
| iam_policies | Shared least-privilege roles and policies. |
| observability | Logs, metrics, dashboards, alarms. |

### Single-command deployment flow
```bash
make deploy ENV=staging
```

### Environment configs
- local
- dev
- staging
- prod

### CI/CD outline
- Run tests and contract checks on pull requests.
- Plan and review Terraform changes before apply.
- Build/publish API and UI artifacts on merge.
- Promote through staging to production with approvals and smoke tests.
- Run scheduled drift detection and publish results.
- Maintain rollback paths for UI, API, and config versions.

## 13. UI/UX Blueprint

- Dashboard
- Topology Map
- Site Detail
- Line Detail
- Asset Detail
- Batch Tracker
- QA Release Board
- CAPA / Deviation Queue
- Dossier Viewer
- Assistant Chat
- Admin Diagnostics

| Component | Purpose |
| --- | --- |
| StatusCard | Compact status, owner, next action, and evidence summary. |
| ReasonCodeList | Displays explainability reasons. |
| ReadinessBar | Score and threshold visualization. |
| TopologyTree | Hierarchical drilldown navigation. |
| WorkflowBoard | Swimlane or queue-based action board. |
| EvidenceChecklist | Required vs present evidence rendering. |
| AssistantAnswerCard | Structured assistant answer with citations. |

### Text wireframes
```text
Dashboard → site cards → readiness bars → workflow highlights → assistant launch
Site Detail → area/line summaries → active blockers → owner/action list
QA Release Board → ready / evidence pending / hold / released columns
```

### Accessibility considerations
- Never rely on color alone for status meaning.
- Support keyboard navigation for boards, tables, tabs, and chat.
- Provide text alternatives for charts and visual summaries.

### Card design standard
- What happened?
- Why does it matter?
- Who owns it?
- What next?
- What evidence?

## 14. API Contracts

| Method | Path | Purpose | Request shape | Response shape |
| --- | --- | --- | --- | --- |
| GET | /cp/sites | List visible sites | {filters?} | {sites: SiteHealthCard[]} |
| GET | /cp/sites/{site_id}/health | Get detailed site posture | {site_id} | {site, readiness, areas} |
| GET | /cp/topology | Get topology nodes and optional flows | {site_id?, include_flows?} | {nodes, edges} |
| GET | /cp/connectors | Get connector health | {site_id?, connector_type?, status?} | {connectors} |
| GET | /cp/readiness | Get readiness scores | {scope?, site_id?, line_id?, batch_id?} | {scores, rollup} |
| GET | /cp/personas/{persona}/workflow | Get persona workflow board | {persona, subject_id?} | {workflow} |
| POST | /cp/assistant/query | Ask bounded assistant question | {question, persona?, site_id?, line_id?, batch_id?} | AssistantResponse |
| GET | /cp/dossiers/{batch_id} | Get dossier status | {batch_id} | {batch_id, dossier_status, completeness, evidence_items, missing_evidence} |
| GET | /cp/capa/queue | Get CAPA/deviation queue | {site_id?, status?, owner?} | {queue, summary} |

All response shapes are domain-safe and must not expose raw AWS IDs.

## 15. Security and Compliance Posture

- IAM least privilege is mandatory for each runtime component.
- Tenant/site isolation must be enforced at data, API, and infrastructure layers.
- Audit logging must capture workflow changes, approvals, evidence changes, and assistant interactions.
- Encryption at rest and in transit is mandatory.
- OT posture remains read-only.
- No automatic GxP decisions are permitted.
- Audit trail design must make all significant actions explainable and reviewable.

## 16. Testing and Validation Plan

| Area | Test level | Goal |
| --- | --- | --- |
| Artifact normalization | Unit + integration | Consistent canonical projection from local and AWS-shaped inputs. |
| Token translation | Unit | Raw tokens always map to approved public labels. |
| Topology rendering | API + UI | Structural and runtime topology render correctly. |
| Data-flow status | Unit + integration | Traffic-light rules are deterministic. |
| Persona API responses | Contract | Role-specific payload shapes remain stable. |
| Assistant response formatting | Unit + integration | Structured output includes citations and compliance note. |
| No-raw-JSON and no infra leakage | Security regression | No forbidden tokens appear in safe responses. |
| Local ingestion | Integration | File watcher updates read models correctly. |
| Cloud source mapping | Integration | AWS production sources map into the same public contracts. |
| API contract stability | Snapshot/contract | Frontend-safe response shapes remain stable. |

### Example unit tests
```python
def test_translation_masks_raw_connector_id():
    assert translate_connector("qms-veeva-vault-live").label == "QMS / Veeva Vault"


def test_rollup_red_when_mandatory_evidence_missing():
    score = compute_line_readiness(...)
    assert score.status == "red"
```

### Example integration tests
```python
def test_persona_workflow_endpoint_returns_qa_release_board(client):
    body = client.get("/cp/personas/qa/workflow").json()
    assert body["workflow"]["view_id"] == "qa-release-board"


def test_assistant_does_not_leak_infra_tokens(client):
    body = client.post("/cp/assistant/query", json={"question": "Why is Line 4 yellow?"}).json()
    assert "arn:aws:" not in body["answer_markdown"]
```

### Operational runbooks
- Connector stale incident runbook.
- Evidence completeness failure runbook.
- Assistant degraded/unavailable runbook.
- Topology translation miss runbook.
- Production rollback runbook.

## 17. Phased Implementation Roadmap

### Phase 1: local read-only observability foundation (4 weeks)

- Normalized models
- Local Postgres + mock ingestion
- Core `/cp` APIs
- Basic React dashboard/topology

**Acceptance criteria:** Deliverables operate via stable, domain-safe contracts and pass designated test and observability gates.

### Phase 2: persona workflow engine (4 weeks)

- Workflow tables
- QA Release Board
- Admin diagnostics
- Plant/engineering views

**Acceptance criteria:** Deliverables operate via stable, domain-safe contracts and pass designated test and observability gates.

### Phase 3: MCP assistant integration (4 weeks)

- MCP tools
- Assistant response schema
- Chat UI
- Leakage/compliance guardrails

**Acceptance criteria:** Deliverables operate via stable, domain-safe contracts and pass designated test and observability gates.

### Phase 4: AWS production deployment (6 weeks)

- Terraform orchestration
- CloudFront/S3 UI
- App Runner API
- Aurora/S3/SiteWise integration
- Observability

**Acceptance criteria:** Deliverables operate via stable, domain-safe contracts and pass designated test and observability gates.

### Phase 5: advanced analytics and multi-site (6 weeks)

- Leadership analytics
- Cross-site benchmarking
- Trend history
- Multi-site templates

**Acceptance criteria:** Deliverables operate via stable, domain-safe contracts and pass designated test and observability gates.

## 18. Acceptance Criteria

1. Domain-safe `/cp/*` endpoints exist and are documented.
2. No raw AWS IDs or source tokens appear in frontend-safe payloads.
3. Local full-stack Docker Compose mode runs successfully.
4. At least one biopharma and one OSD/API topology template render correctly.
5. Readiness rollups are deterministic and explainable.
6. All five personas have distinct workflow views.
7. Assistant responses are MCP-grounded, structured, and compliant.
8. QA release remains human-approved.
9. No silent failures occur for connectors or pipeline degradation.
10. CI enforces contract, leakage, and regression tests.

## 19. Concrete Next Engineering Tasks

| Priority | Owner persona/team | Task | Acceptance criteria |
| --- | --- | --- | --- |
| P0 | Platform | Expand Docker Compose to api/ui/postgres/mock-ingestion-engine/mcp-server | Single-command startup works. |
| P0 | Backend | Define new normalized Pydantic models | Models are used by `/cp/*` routes and tested. |
| P0 | Backend | Implement translation catalog service | Leakage tests pass. |
| P0 | Backend | Create core `/cp/sites`, `/cp/topology`, `/cp/connectors`, `/cp/readiness` routes | Routes match contract snapshots. |
| P0 | Backend | Persist local read models in Postgres | API stops depending on artifact folder traversal at request time. |
| P1 | Frontend | Bootstrap React/TypeScript app | Dashboard loads from local API. |
| P1 | Frontend | Implement Dashboard, Site Detail, and Line Detail | Drilldown works with preserved context. |
| P1 | Backend | Implement readiness scoring engine and reason codes | Rollups are deterministic and tested. |
| P1 | Backend | Implement persona workflow endpoints and tables | Each role gets a tailored workflow payload. |
| P1 | Backend | Implement dossier and CAPA queue read models | QA views show evidence gaps and blockers. |
| P1 | Platform | Define Terraform root composition for app modules | Staging plan succeeds. |
| P2 | Backend | Build mock-ingestion-engine file watcher | Editing mock files updates state deterministically. |
| P2 | Frontend | Build QA Release Board and Dossier Viewer | QA can inspect completeness, evidence, and approvals. |
| P2 | Backend | Introduce MCP tool server contracts | Assistant endpoint uses approved tools only. |
| P2 | Security | Add raw-token leakage regression tests | CI fails on disallowed tokens. |
| P2 | Platform | Wire CloudWatch metrics/alarms | Staging dashboards and alarms exist. |
| P3 | Frontend | Build Admin Diagnostics and Connector Health views | Admins can inspect pipeline and mapping posture. |
| P3 | Backend | Add trend endpoints for leadership analytics | Leadership dashboard can render history. |
| P3 | Compliance | Formalize human-approval audit trail | Approval events are recorded with actor/time/evidence context. |
| P3 | Platform | Automate deploy/promotion/rollback flow | Promotion to staging/prod is reproducible and smoke-tested. |

## Appendix A. Domain Vocabulary Reference

- **Enterprise posture:** Overall multi-site state computed from site rollups and cross-site risk dimensions.
- **Readiness:** Deterministic measure of preparedness for a business action.
- **Evidence completeness:** Whether required records and documents are present and traceable.
- **Dossier:** Assembled package of evidence, analysis, and workflow context.
- **Workflow item:** Unit of actionable work owned by a persona.
- **Translation catalog:** Governed mapping from raw source tokens to business-safe labels.
- **Topology registry:** Master model of enterprise/site/area/line/cell/asset structure.
- **Data-flow edge:** Directional dependency or telemetry movement relationship between nodes.
- **Reason code:** Machine-stable explanation code for a status or score outcome.
- **Hard stop:** Condition that forces red status regardless of weighted averages.

## Appendix B. Requirement-by-Concern Notes

### Architecture

1. Read-only-first OT integrations.
2. Layered boundary between source systems and user experience.
3. Same public contracts in local and AWS modes.

### Data modeling

1. Stable public IDs.
2. Freshness timestamps.
3. Reason codes on scored entities.

### Workflow

1. Ownership fields.
2. SLA state.
3. Action history.

### Assistant

1. MCP tool boundary.
2. Citations.
3. Human-approval note.

### Security

1. Least privilege.
2. Audit logging.
3. Token masking.

### Testing

1. Contract tests.
2. Leakage tests.
3. Integration coverage for mock and AWS-shaped inputs.

## Appendix C. Detailed Implementation Guidance Matrix

### Guidance Item 1: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 2: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 3: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 4: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 5: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 6: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 7: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 8: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 9: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 10: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 11: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 12: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 13: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 14: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 15: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 16: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 17: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 18: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 19: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 20: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 21: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 22: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 23: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 24: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 25: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 26: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 27: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 28: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 29: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 30: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 31: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 32: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 33: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 34: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 35: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 36: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 37: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 38: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 39: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 40: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 41: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 42: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 43: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 44: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 45: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 46: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 47: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 48: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 49: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 50: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 51: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 52: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 53: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 54: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 55: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 56: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 57: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 58: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 59: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 60: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 61: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 62: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 63: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 64: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 65: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 66: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 67: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 68: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 69: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 70: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 71: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 72: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 73: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 74: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 75: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 76: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 77: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 78: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 79: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 80: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 81: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 82: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 83: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 84: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 85: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 86: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 87: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 88: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 89: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 90: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 91: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 92: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 93: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 94: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 95: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 96: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 97: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 98: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 99: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 100: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 101: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 102: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 103: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 104: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 105: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 106: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 107: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 108: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 109: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 110: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 111: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 112: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 113: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 114: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 115: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 116: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 117: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 118: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 119: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 120: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 121: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 122: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 123: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 124: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 125: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 126: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 127: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 128: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 129: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 130: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 131: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 132: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 133: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 134: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 135: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 136: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 137: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 138: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 139: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 140: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 141: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 142: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 143: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 144: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 145: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 146: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 147: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 148: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 149: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 150: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 151: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 152: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 153: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 154: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 155: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 156: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 157: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 158: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 159: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 160: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 161: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 162: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 163: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 164: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 165: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 166: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 167: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 168: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 169: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 170: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 171: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 172: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 173: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 174: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 175: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 176: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 177: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 178: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 179: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 180: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 181: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 182: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 183: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 184: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 185: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 186: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 187: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 188: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 189: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 190: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 191: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 192: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 193: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 194: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 195: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 196: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 197: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 198: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 199: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 200: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 201: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 202: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 203: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 204: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 205: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 206: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 207: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 208: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 209: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 210: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 211: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 212: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 213: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 214: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 215: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 216: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 217: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 218: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 219: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 220: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 221: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 222: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 223: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 224: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 225: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 226: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 227: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 228: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 229: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 230: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 231: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 232: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 233: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 234: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 235: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 236: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 237: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 238: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 239: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 240: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 241: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 242: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 243: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 244: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 245: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 246: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 247: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 248: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 249: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 250: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 251: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 252: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 253: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 254: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 255: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 256: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 257: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 258: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 259: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 260: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 261: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 262: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 263: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 264: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 265: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 266: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 267: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 268: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 269: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 270: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 271: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 272: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 273: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 274: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 275: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 276: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 277: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 278: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 279: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 280: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 281: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 282: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 283: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 284: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 285: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 286: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 287: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 288: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 289: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 290: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 291: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 292: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 293: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 294: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 295: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 296: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 297: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 298: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 299: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 300: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 301: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 302: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 303: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 304: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 305: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 306: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 307: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 308: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 309: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 310: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 311: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 312: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 313: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 314: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 315: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 316: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 317: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 318: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 319: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 320: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 321: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 322: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 323: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 324: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 325: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 326: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 327: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 328: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 329: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 330: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 331: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 332: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 333: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 334: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 335: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 336: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 337: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 338: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 339: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 340: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

### Guidance Item 341: Domain Translation
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `public API schema` for domain translation.
- Architectural concern: prevent raw token leakage while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass API contract tests before promoting the change across environments.

### Guidance Item 342: Connector Health
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Pydantic model` for connector health.
- Architectural concern: prevent hidden freshness breach while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass token leakage regression tests before promoting the change across environments.

### Guidance Item 343: Topology Modeling
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `read-model table` for topology modeling.
- Architectural concern: prevent unclear ownership while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass persona workflow acceptance tests before promoting the change across environments.

### Guidance Item 344: Line Readiness
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `React page` for line readiness.
- Architectural concern: prevent non-deterministic rollup while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass topology rendering tests before promoting the change across environments.

### Guidance Item 345: Batch Release
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `workflow board` for batch release.
- Architectural concern: prevent assistant hallucination while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass assistant citation tests before promoting the change across environments.

### Guidance Item 346: Dossier Assembly
- Primary owner: Platform.
- Deliverable emphasis: strengthen the `assistant tool contract` for dossier assembly.
- Architectural concern: prevent workflow dead-end while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass score rollup unit tests before promoting the change across environments.

### Guidance Item 347: Capa Workflow
- Primary owner: Backend.
- Deliverable emphasis: strengthen the `Terraform module` for CAPA workflow.
- Architectural concern: prevent topology drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass local-vs-cloud mapping tests before promoting the change across environments.

### Guidance Item 348: Admin Diagnostics
- Primary owner: Frontend.
- Deliverable emphasis: strengthen the `CloudWatch alarm` for admin diagnostics.
- Architectural concern: prevent evidence ambiguity while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass observability smoke tests before promoting the change across environments.

### Guidance Item 349: Assistant Grounding
- Primary owner: Quality Systems.
- Deliverable emphasis: strengthen the `integration adapter` for assistant grounding.
- Architectural concern: prevent connector blind spot while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass access-control checks before promoting the change across environments.

### Guidance Item 350: Aws Deployment
- Primary owner: Engineering Reliability.
- Deliverable emphasis: strengthen the `test fixture` for AWS deployment.
- Architectural concern: prevent deployment drift while preserving domain-safe control-plane behavior.
- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.
- Verification gate: pass audit-trail validation before promoting the change across environments.

## Appendix D. Source-System-to-Control-Plane Mapping Notes

### Historian / Ignition

- Source inputs: asset telemetry, alarms, environmental measurements.
- Control-plane outputs: asset health, data freshness, topology telemetry edges.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.

### QMS / Veeva Vault

- Source inputs: deviations, quality events, approvals.
- Control-plane outputs: CAPA queue, QA release readiness, audit readiness.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.

### MES / PharmaSuite

- Source inputs: batch timeline, operation phase, status transitions.
- Control-plane outputs: batch tracker, line readiness, dossier context.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.

### LIMS / LabWare

- Source inputs: lab results, sample outcomes, release-supporting QC records.
- Control-plane outputs: batch release, dossier completeness, audit evidence.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.

### CMMS / Maximo or Infor EAM

- Source inputs: work orders, asset maintenance history.
- Control-plane outputs: engineering workflow, asset reliability, risk posture.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.

### ERP / SAP

- Source inputs: genealogy, material, campaign and planning context.
- Control-plane outputs: batch/product context, leadership summaries, lineage.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.

### MQTT / OPC-UA edge feeds

- Source inputs: industrial event streams and interoperability signals.
- Control-plane outputs: connector health, telemetry routing, local simulation.
- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.
- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.
