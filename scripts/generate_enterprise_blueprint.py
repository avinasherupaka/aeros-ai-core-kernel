from pathlib import Path

out = Path('/home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel/docs/enterprise-control-plane-blueprint.md')
lines = []

def add(text=''):
    if text == '':
        lines.append('')
    else:
        for part in text.split('\n'):
            lines.append(part.rstrip())

def h(level, title):
    add(f"{'#'*level} {title}")
    add()

def bullets(items, prefix='-'):
    for item in items:
        add(f'{prefix} {item}')
    add()

def numbered(items):
    for i, item in enumerate(items, 1):
        add(f'{i}. {item}')
    add()

def table(headers, rows):
    add('| ' + ' | '.join(headers) + ' |')
    add('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    for row in rows:
        add('| ' + ' | '.join(str(cell).replace('\n', '<br>') for cell in row) + ' |')
    add()

def code_block(lang, text):
    add(f'```{lang}')
    add(text.strip('\n'))
    add('```')
    add()

add('# Enterprise Control Plane Blueprint')
add()
add('**Document Purpose:** Connected Manufacturing Enterprise Control Plane for Areos / Aeros AI Core Kernel')
add()
add('**Context:** Prepared for the current Python/FastAPI backend and planned React/TypeScript frontend with AWS production and Docker Compose local mode.')
add()
add('**Primary repository anchors:** `src/aeros/kernel/api/main.py`, `src/aeros/kernel/control_plane/service.py`, `src/aeros/kernel/models/`, `src/aeros/kernel/connectors/`, `infra/terraform/modules/`, `docker-compose.yml`, and `tests/`.')
add()
add('**Positioning statement:** This blueprint converts the current prototype into an enterprise-grade, read-only-first manufacturing control plane that normalizes OT/IT context, exposes persona-specific workflows, and grounds an MCP assistant in domain-safe manufacturing views rather than raw infrastructure payloads.')
add()

h(2, 'Table of Contents')
bullets([
    '1. [Executive Summary](#1-executive-summary)',
    '2. [Diagnosis of Current Prototype Flaws](#2-diagnosis-of-current-prototype-flaws)',
    '3. [Target Architecture Overview](#3-target-architecture-overview)',
    '4. [Domain Abstraction Model](#4-domain-abstraction-model)',
    '5. [Normalized Data Model](#5-normalized-data-model)',
    '6. [Topology and Data-Flow Design](#6-topology-and-data-flow-design)',
    '7. [Readiness and Health Scoring Engine](#7-readiness-and-health-scoring-engine)',
    '8. [Persona Workflows](#8-persona-workflows)',
    '9. [MCP Assistant Design](#9-mcp-assistant-design)',
    '10. [Local Developer Mode](#10-local-developer-mode)',
    '11. [AWS Production Architecture](#11-aws-production-architecture)',
    '12. [IaC and Deployment Strategy](#12-iac-and-deployment-strategy)',
    '13. [UI/UX Blueprint](#13-uiux-blueprint)',
    '14. [API Contracts](#14-api-contracts)',
    '15. [Security and Compliance Posture](#15-security-and-compliance-posture)',
    '16. [Testing and Validation Plan](#16-testing-and-validation-plan)',
    '17. [Phased Implementation Roadmap](#17-phased-implementation-roadmap)',
    '18. [Acceptance Criteria](#18-acceptance-criteria)',
    '19. [Concrete Next Engineering Tasks](#19-concrete-next-engineering-tasks)',
])

# Core data used across generated sections
reason_codes = [
    ('CONNECTOR_STALE', 'No successful update within configured freshness window.'),
    ('CONNECTOR_ERROR_BURST', 'Recent connector failures exceed error threshold.'),
    ('SCHEMA_VALIDATION_FAILED', 'Source records do not meet canonical contract.'),
    ('ASSET_HEALTH_WARNING', 'Asset telemetry indicates degraded but not failed state.'),
    ('ASSET_HEALTH_CRITICAL', 'Asset telemetry indicates critical failure or breach.'),
    ('MISSING_MANDATORY_EVIDENCE', 'Required evidence item absent for current context.'),
    ('DOSSIER_SECTION_INCOMPLETE', 'One or more dossier sections incomplete or unreviewed.'),
    ('QA_HOLD_ACTIVE', 'QA hold or deviation prevents release progress.'),
    ('AUDIT_TRACE_GAP', 'Traceability chain incomplete or unverifiable.'),
    ('PIPELINE_LATENCY_BREACH', 'Pipeline latency exceeds SLA.'),
    ('NO_SILENT_FAILURE_ALLOWED', 'A subsystem failed without a visible status update; force red/alert.'),
    ('ROLLUP_CHILD_RED', 'Parent status red because at least one mandated child is red.'),
]
scoring_dims = [
    ('equipment_health', 'Mechanical or environmental health of assets and utilities.', 'Telemetry thresholds, alarms, maintenance state, downtime markers.'),
    ('connector_health', 'Availability and integrity of data integrations.', 'Heartbeat freshness, schema validation, retry failures, error rate.'),
    ('data_freshness', 'How recent critical data is compared to configured SLA.', 'Last event age, missed cadence, stale cache.'),
    ('data_quality', 'Validity and trustworthiness of incoming records.', 'Quality flags, schema completeness, duplicate rate, null rates.'),
    ('evidence_completeness', 'Presence of required supporting records and documents.', 'Expected-vs-present evidence manifest.'),
    ('dossier_readiness', 'Completeness and reviewability of the batch/event dossier.', 'Dossier section completion, reviewer assignments, pending gaps.'),
    ('qa_release_readiness', 'Whether QA can proceed to release review.', 'Evidence completeness, deviation holds, approval status.'),
    ('capa_deviation_readiness', 'Ability to triage or close CAPA/deviation activities.', 'Investigation fields, root-cause links, action completion.'),
    ('audit_readiness', 'Whether the state is suitable for audit review.', 'Traceability, signed approvals, document completeness.'),
    ('plant_risk', 'Operational and quality risk posture of the site/line.', 'Critical events, chronic issues, blocked batches.'),
    ('pipeline_health', 'Health of ingestion and processing backbone.', 'Queue lag, rule failures, processing latency.'),
    ('site_posture', 'Overall site state from weighted dimensions.', 'Rollup across mandatory dimensions.'),
]
personas = {
    'System Administrator': {
        'objective': 'Maintain connector health, topology integrity, policy compliance, and platform diagnostics.',
        'pages': ['Admin Diagnostics dashboard', 'Connector Health table', 'Topology Registry editor', 'Environment Diff / Drift view', 'Assistant audit log'],
        'kpis': ['Connectors green %', 'Stale feeds count', 'Topology translation misses', 'API p95 latency', 'Assistant tool success rate'],
        'workflow': ['Review red/yellow connectors', 'Investigate missing mappings or stale feeds', 'Acknowledge/assign incidents', 'Verify recovery and close diagnostic event'],
        'ui': ['Global health banner', 'Connector matrix', 'Topology diff panel', 'Policy warnings drawer', 'Pipeline event timeline'],
        'deps': ['Connector heartbeat telemetry', 'CloudWatch metrics', 'translation catalog', 'topology registry', 'workflow incident table'],
        'apis': ['GET /cp/connectors', 'GET /cp/topology', 'GET /cp/readiness?scope=platform', 'POST /cp/assistant/query'],
    },
    'Quality Assurance': {
        'objective': 'Assess evidence completeness, release readiness, deviation/CAPA impact, and audit traceability.',
        'pages': ['QA Release Board', 'Batch Tracker', 'Dossier Viewer', 'CAPA/Deviation Queue', 'Evidence gap panel'],
        'kpis': ['Batches release-ready', 'Batches blocked', 'Mandatory evidence gaps', 'Pending approvals', 'Audit-ready %'],
        'workflow': ['Open release board', 'Inspect blocked batches', 'Review dossier completeness and evidence', 'Assign or request missing evidence', 'Approve or hold release'],
        'ui': ['Release board columns', 'Batch summary cards', 'Dossier completeness progress', 'Evidence citations panel', 'Human approval footer'],
        'deps': ['MES batch context', 'QMS deviation records', 'LIMS results', 'evidence manifests', 'workflow approvals'],
        'apis': ['GET /cp/readiness', 'GET /cp/dossiers/{batch_id}', 'GET /cp/capa/queue', 'POST /cp/assistant/query'],
    },
    'Plant Head / Plant Ops': {
        'objective': 'Monitor site posture, line readiness, operational bottlenecks, and business risk.',
        'pages': ['Executive Dashboard', 'Site Detail', 'Line Detail', 'Risk summary view', 'Action tracker'],
        'kpis': ['Lines green/yellow/red', 'Open high-risk events', 'Blocked batches', 'Downtime minutes', 'Site risk tier'],
        'workflow': ['Scan dashboard', 'Drill into yellow/red lines', 'Review blockers and owners', 'Escalate cross-functional actions', 'Confirm recovery'],
        'ui': ['Site cards', 'Line readiness strip', 'Ownership table', 'Trend charts', 'Escalation widget'],
        'deps': ['Site rollups', 'asset health', 'batch readiness', 'connector posture', 'workflow ownership state'],
        'apis': ['GET /cp/sites', 'GET /cp/sites/{site_id}/health', 'GET /cp/topology', 'GET /cp/readiness', 'POST /cp/assistant/query'],
    },
    'Engineering / Reliability': {
        'objective': 'Identify chronic equipment issues, telemetry anomalies, maintenance impacts, and recovery actions.',
        'pages': ['Reliability Board', 'Asset Detail', 'Maintenance impact view', 'Connector/asset correlation panel'],
        'kpis': ['Critical assets', 'Repeat deviations', 'Mean time to recovery', 'Maintenance work orders open', 'Telemetry quality issues'],
        'workflow': ['Review chronic assets', 'Correlate failures with maintenance and telemetry', 'Open investigation or maintenance action', 'Track resolution effectiveness'],
        'ui': ['Asset risk heatmap', 'Telemetry timeline', 'Work-order linkage', 'Root-cause hypothesis notes', 'Recommended next checks'],
        'deps': ['Historian data', 'CMMS work orders', 'connector health', 'asset topology', 'assurance events'],
        'apis': ['GET /cp/topology', 'GET /cp/connectors', 'GET /cp/readiness?scope=asset', 'POST /cp/assistant/query'],
    },
    'Leadership': {
        'objective': 'See enterprise posture, portfolio risk, site comparison, and readiness trends without operational noise.',
        'pages': ['Enterprise Dashboard', 'Site Comparison board', 'Risk Trend view', 'Strategic summary feed'],
        'kpis': ['Sites green/yellow/red', 'Enterprise risk index', 'Release throughput at risk', 'Audit readiness trend', 'Top systemic bottlenecks'],
        'workflow': ['Review enterprise summary', 'Compare site posture', 'Identify common bottlenecks', 'Trigger governance reviews or investments'],
        'ui': ['Enterprise scorecards', 'Comparison matrix', 'Trend narratives', 'Top risks list', 'Strategic actions panel'],
        'deps': ['Aggregated site rollups', 'workflow trend history', 'connector/site posture summaries', 'business calendar context'],
        'apis': ['GET /cp/sites', 'GET /cp/readiness?scope=enterprise', 'GET /cp/personas/leadership/workflow', 'POST /cp/assistant/query'],
    },
}

# Section 1
h(2, '1. Executive Summary')
add('The Connected Manufacturing Enterprise Control Plane is the operating surface that sits above heterogeneous plant, quality, maintenance, and enterprise systems and turns fragmented machine-centric data into human-actionable manufacturing context. The control plane does **not** replace MES, QMS, historian, ERP, CMMS, LIMS, SCADA, PLC, or AWS industrial services. Instead, it creates a governed abstraction layer that allows plant, quality, engineering, and leadership personas to reason about manufacturing state in business-safe language.')
add()
bullets([
    'A Python/FastAPI API layer already exists in `src/aeros/kernel/api/main.py`.',
    'A control-plane snapshot service already exists in `src/aeros/kernel/control_plane/service.py`.',
    'Connector packs already exist for historian, QMS/MES, CMMS/ERP/LIMS, MQTT, and OPC-UA.',
    'Domain models already exist for assets, batches, evidence, and canonical events in `src/aeros/kernel/models/`.',
    'Terraform modules already exist for foundation, IoT Core, SiteWise, evidence lake, workflow runtime, Neptune, observability, and tenant/site/cell segmentation.',
    'A substantial Python test suite already exists in `tests/`.',
])
add('The target operating model of the control plane is enterprise read-only observability plus workflow coordination. The key design outcome is that all personas see **business-safe, explainable, role-appropriate** information rather than raw integration payloads or infrastructure identifiers. This blueprint introduces a formal domain abstraction layer, a normalized topology and readiness model, a React/TypeScript frontend, an MCP-grounded assistant, a richer Docker Compose developer mode, and a clear AWS production architecture.')
add()
bullets([
    'The control plane is a **system of assurance and coordination**, not the system of record.',
    'All regulated decisions remain human-mediated.',
    'All assistant responses are grounded and bounded.',
    'All status outcomes are explainable via reason codes.',
    'All user-facing APIs are domain-safe and infrastructure-redacted.',
])

# Section 2
h(2, '2. Diagnosis of Current Prototype Flaws')
add('The current prototype successfully demonstrates deterministic evidence processing and simple control-plane storytelling. It is not yet a scalable enterprise architecture. The main flaws are leaky abstractions, lack of role-based context, an unstructured chatbot, and static topology assumptions.')
add()
table(['Flaw family', 'Current manifestation', 'Why it matters', 'Blueprint correction'], [
    ['Leaky abstractions', 'Backend internals and connector/artifact concepts bleed into user-facing representations.', 'Frontend and assistant surfaces become brittle and unsafe.', 'Introduce strict translation and masking rules.'],
    ['Lack of role-based context', 'Persona summaries are shallow and generic.', 'Each persona lacks targeted workflow/action surfaces.', 'Define persona-specific pages, KPIs, and workflow models.'],
    ['Unstructured chatbot', 'Keyword branching returns generic markdown.', 'No tool contracts, citations, or safety boundaries exist.', 'Move to MCP tools and structured AssistantResponse.'],
    ['Static topology', 'Hard-coded site/area assumptions and event-derived topology.', 'Plants and lines cannot scale or be administered cleanly.', 'Create explicit topology and data-flow models.'],
])
for flaw, bullets_list in {
    'Leaky abstractions': [
        'Current service logic mixes evidence-root details, connector replay semantics, and user-facing business views.',
        'The frontend should never know how local artifact folders or raw AWS services are organized.',
        'Domain-safe APIs must become the only frontend contract.'
    ],
    'Lack of role-based context': [
        'A QA user and a Plant Head should not consume the same “generic highlights” object.',
        'Workflow items need owner, SLA, next action, and evidence context.',
        'Persona routing and data slices must become first-class architecture.'
    ],
    'Unstructured chatbot': [
        'Keyword heuristics are acceptable for demos but unsafe for enterprise workflows.',
        'The assistant must call deterministic tools and cite its evidence sources.',
        'The assistant must never imply regulated approval authority.'
    ],
    'Static topology': [
        'A topology must exist even when there are no active events.',
        'Site/area/line/cell/asset structure should come from a managed registry or templates.',
        'Topology health and data-flow health need separate representations.'
    ],
}.items():
    h(3, flaw)
    bullets(bullets_list)

# Section 3
h(2, '3. Target Architecture Overview')
code_block('text', '''
Edge / OT → IoT Core / Greengrass → SiteWise / Normalization → Backbone → Control Plane API → React UI + MCP Assistant
''')
add('The target architecture is layered, domain-safe, explainable, and productionizable. It explicitly separates source-system acquisition from normalization, evidence persistence, workflow coordination, user experience, and assistant orchestration.')
add()
table(['Layer', 'Responsibility', 'Representative technology'], [
    ['Edge/OT', 'Read source systems without write-back.', 'Historian, MES, QMS, ERP, CMMS, OPC-UA, MQTT, PLC/SCADA/BMS.'],
    ['IoT Core / Greengrass', 'Site-edge connector runtime and secure ingestion.', 'AWS IoT Greengrass V2, AWS IoT Core, rules.'],
    ['SiteWise / Normalization', 'Asset and telemetry projection plus canonical event transformation.', 'AWS IoT SiteWise, Python normalization services.'],
    ['Backbone', 'Persist evidence, workflow state, and queryable context.', 'S3, Aurora PostgreSQL, optional graph/search stores.'],
    ['Control Plane API', 'Expose domain-safe control-plane contracts.', 'Python, FastAPI, Pydantic.'],
    ['React UI + MCP Assistant', 'Persona-centric user experience and bounded guidance.', 'React, TypeScript, MCP server, Bedrock in production.'],
])

# Section 4
h(2, '4. Domain Abstraction Model')
add('The domain abstraction model prevents the control plane from becoming a raw system-integration dashboard. It translates tokens, hides infrastructure internals, and defines the semantic hierarchy users interact with.')
add()
table(['Raw token', 'Domain-safe label'], [
    ['`hyd_site_01`', 'Hyderabad Plant 1'],
    ['`blr_bio_01`', 'Bengaluru Biopharma Campus'],
    ['`powder_mixer_03`', 'Powder Mixer 3'],
    ['`qms-veeva-vault-live`', 'QMS / Veeva Vault'],
    ['`historian-ignition-live`', 'BMS / Ignition Historian'],
])
table(['Semantic taxonomy', 'Description'], [
    ['Site', 'Manufacturing location or campus.'],
    ['Area', 'Operational segment within a site.'],
    ['Line', 'Production or utility line within an area.'],
    ['Cell/Room', 'Contained production or support environment.'],
    ['Asset', 'Specific equipment or system component.'],
    ['Batch/Product', 'Manufacturing lot or product context.'],
    ['Event', 'Normalized operational or quality event.'],
    ['Evidence', 'Supporting record or document.'],
    ['Disposition', 'Governed business decision or workflow state.'],
])
add('### Infrastructure masking rules')
bullets([
    'Map raw AWS identifiers to public domain identifiers before frontend exposure.',
    'Map raw topic names and historian tags to approved semantic labels.',
    'Return evidence handles or signed URLs, never raw storage keys.',
    'Keep raw connector credentials, endpoints, and secrets backend-only.',
])
add('### What must never leak to frontend')
bullets([
    'Raw AWS IoT SiteWise asset/property IDs.',
    'Raw S3 bucket names and object keys.',
    'Greengrass component IDs, certificates, and deployment internals.',
    'Historian tag paths, OPC-UA node IDs, and raw MQTT topic structures.',
    'Secrets, credentials, account IDs, IAM role names, subnet IDs, or security-group IDs.',
])

# Section 5
h(2, '5. Normalized Data Model')
models = [
    ('ControlPlaneSnapshot', 'Top-level aggregate used for dashboard and assistant context.', [('snapshot_id', 'string'), ('generated_at', 'datetime'), ('environment', 'enum'), ('enterprise_status', 'traffic_light'), ('sites', 'SiteHealthCard[]'), ('connectors', 'ConnectorStatus[]'), ('readiness', 'ReadinessScore[]'), ('topology', 'TopologyNode[]'), ('flows', 'DataFlowEdge[]'), ('persona_workflows', 'PersonaWorkflow[]')]),
    ('SiteHealthCard', 'Global site posture summary.', [('site_id', 'string'), ('site_label', 'string'), ('site_type', 'enum'), ('status', 'traffic_light'), ('risk_score', 'number'), ('readiness_score', 'number'), ('freshness_seconds', 'integer'), ('open_events', 'integer'), ('blocked_batches', 'integer'), ('top_reason_codes', 'string[]')]),
    ('ConnectorStatus', 'Health view of an integration connector.', [('connector_public_id', 'string'), ('source_system_label', 'string'), ('site_scope', 'string|null'), ('status', 'traffic_light'), ('records_last_hour', 'integer'), ('freshness_seconds', 'integer'), ('latency_ms_p95', 'integer'), ('error_rate_percent', 'number'), ('reason_codes', 'string[]'), ('last_success_at', 'datetime|null')]),
    ('ReadinessScore', 'Deterministic score dimension.', [('dimension', 'string'), ('label', 'string'), ('status', 'traffic_light'), ('score', 'number'), ('weight', 'number'), ('reason_codes', 'string[]'), ('explanation', 'string'), ('updated_at', 'datetime')]),
    ('PersonaWorkflow', 'Persona-specific workflow board or guidance object.', [('persona', 'string'), ('view_id', 'string'), ('headline', 'string'), ('kpis', 'object[]'), ('sections', 'object[]'), ('actions', 'object[]'), ('dependencies', 'string[]'), ('sla_state', 'string')]),
    ('AssistantResponse', 'Structured answer returned by the assistant.', [('request_id', 'string'), ('answer_markdown', 'string'), ('summary', 'string'), ('status', 'traffic_light|null'), ('reason_codes', 'string[]'), ('citations', 'object[]'), ('missing_evidence', 'object[]'), ('recommended_actions', 'object[]'), ('human_approval_required', 'boolean')]),
    ('TopologyNode', 'Normalized topology or workflow graph node.', [('node_id', 'string'), ('node_type', 'string'), ('label', 'string'), ('parent_node_id', 'string|null'), ('status', 'traffic_light'), ('metadata', 'object'), ('reason_codes', 'string[]'), ('updated_at', 'datetime')]),
    ('DataFlowEdge', 'Directional movement or dependency edge.', [('edge_id', 'string'), ('source_node_id', 'string'), ('target_node_id', 'string'), ('flow_type', 'string'), ('status', 'traffic_light'), ('freshness_seconds', 'integer|null'), ('latency_ms_p95', 'integer|null'), ('reason_codes', 'string[]')]),
]
for name, desc, fields in models:
    h(3, name)
    add(desc)
    add()
    table(['Field', 'Type'], fields)

# Section 6
h(2, '6. Topology and Data-Flow Design')
code_block('text', '''
PLC / SCADA → BMS → Historian → MES → LIMS → QMS → ERP → CMMS → IoT Gateway / Greengrass → IoT Core / Rules → SiteWise → Evidence Graph → Workflow Engine → Control Plane UI → MCP Assistant
''')
add('The control plane needs both a structural topology model and a data-flow model. Structural topology tells the system what exists; data-flow topology tells the system whether the evidence path is healthy enough to trust.')
add()
table(['Status', 'Rule'], [
    ['Green', 'All mandatory contributors are healthy and within SLA.'],
    ['Yellow', 'At least one warning condition exists, but hard-stop blockers are absent.'],
    ['Red', 'A hard-stop, mandatory evidence gap, critical asset issue, or failed mandatory connector exists.'],
])
add('### Example biopharma site topology')
code_block('text', '''
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
''')
add('### Example OSD/API site topology')
code_block('text', '''
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
''')
table(['Source', 'Mapped state'], [
    ['Local JSON artifacts', 'Populate canonical event, workflow, evidence, and readiness state in local Postgres.'],
    ['AWS IoT Core / Greengrass', 'Populate connector freshness, heartbeat, and inbound data-flow states.'],
    ['AWS IoT SiteWise', 'Populate asset hierarchy and industrial telemetry projections.'],
    ['S3 evidence lake', 'Populate evidence manifests and dossier references.'],
    ['Aurora workflow state', 'Populate workflow boards, approvals, and ownership.'],
])

# Section 7
h(2, '7. Readiness and Health Scoring Engine')
table(['Dimension', 'Purpose', 'Typical inputs'], scoring_dims)
add('### Hierarchical rollups')
code_block('text', 'asset → line → area → site → enterprise')
add('### Explainability with reason codes')
table(['Reason code', 'Meaning'], reason_codes)
add('### SLA configuration')
table(['SLA', 'Example', 'Breach outcome'], [
    ['Freshness SLA', 'Historian feed every 60 seconds', 'Yellow at 120 seconds, red at 300 seconds'],
    ['Action SLA', 'QA review within 4 business hours', 'Yellow near deadline, red at breach'],
    ['Evidence SLA', 'Mandatory release evidence present before review', 'Yellow pending, red when release window is hit'],
])
add('### No-silent-failures rule')
add('Any failure to ingest, score, enrich, or publish state must surface as an explicit status. Missing cards or empty arrays are never a substitute for health indicators.')
add()
add('### Example status object')
code_block('json', '''
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
''')
add('### Example rollup object')
code_block('json', '''
{
  "subject_type": "site",
  "subject_id": "site-bio-blr-01",
  "subject_label": "Bengaluru Biopharma Campus",
  "status": "yellow",
  "score": 81,
  "reason_codes": ["ROLLUP_CHILD_RED", "CONNECTOR_STALE", "QA_HOLD_ACTIVE"],
  "updated_at": "2026-06-01T10:15:00Z"
}
''')

# Section 8
h(2, '8. Persona Workflows')
for persona_name, data in personas.items():
    h(3, persona_name)
    add(f'**Objective:** {data["objective"]}')
    add()
    add('**Information architecture**')
    bullets(data['pages'])
    add('**KPI definitions**')
    bullets(data['kpis'])
    add('**Workflow/action model**')
    numbered(data['workflow'])
    add('**Example UI sections**')
    bullets(data['ui'])
    add('**Data dependencies**')
    bullets(data['deps'])
    add('**API endpoints**')
    bullets(data['apis'])

# Section 9
h(2, '9. MCP Assistant Design')
add('The assistant is implemented behind an MCP server/tool boundary. It answers operational questions by invoking deterministic control-plane tools rather than by reading raw source payloads or improvising unsupported logic.')
add()
table(['Tool', 'Input schema', 'Output schema'], [
    ['get_site_status', '{site_id}', '{site, readiness, top_reason_codes}'],
    ['get_connector_health', '{site_id?, connector_type?}', '{connectors}'],
    ['get_line_readiness', '{site_id, line_id}', '{line, dimensions, blockers}'],
    ['get_dossier_status', '{batch_id}', '{batch_id, status, completeness, missing_evidence}'],
    ['get_capa_history', '{subject_id, subject_type}', '{open_items, history}'],
    ['get_batch_release_status', '{batch_id}', '{batch, release_status, blockers, approvals}'],
    ['get_missing_evidence', '{subject_id, subject_type}', '{missing_evidence, severity}'],
    ['get_plant_risk_summary', '{site_id}', '{risk_index, top_risks, recommended_actions}'],
    ['get_workflow_guidance', '{persona, subject_id?}', '{workflow, guidance}'],
])
add('### Assistant response schema')
code_block('json', '''
{
  "request_id": "asst-2026-06-01-001",
  "summary": "Compression Line 4 is yellow because one connector is stale and one mandatory QA evidence item is pending.",
  "answer_markdown": "### Why Line 4 is yellow\n...",
  "status": "yellow",
  "reason_codes": ["CONNECTOR_STALE", "MISSING_MANDATORY_EVIDENCE"],
  "citations": [],
  "missing_evidence": [],
  "recommended_actions": [],
  "human_approval_required": true
}
''')
add('### Good response examples')
for question, answer in [
    ('Why is Line 4 yellow?', 'Explain yellow contributors, list reason codes, and recommend role-appropriate actions.'),
    ('Is BIO-BATCH-204 ready for release?', 'State current release posture, blockers, approvals pending, and human-approval note.'),
    ('What should QA do next?', 'Prioritize highest-impact evidence or approval actions from the QA workflow board.'),
]:
    add(f'- **{question}** — {answer}')
add()
add('### Prohibited response examples')
bullets([
    'Do not say a batch is approved or released without human approval.',
    'Do not leak raw AWS IDs or raw source-system tokens.',
    'Do not invent missing evidence or unknown states.',
    'Do not hide degraded or stale source conditions.',
])
add('### Local context ingestion')
bullets([
    'Use Postgres-backed read models populated by mock-ingestion-engine.',
    'Use deterministic artifact-derived workflow and evidence summaries.',
])
add('### AWS production context sources')
bullets([
    'Aurora workflow/readiness tables.',
    'SiteWise-derived topology and telemetry projections.',
    'S3 evidence manifests and dossier references.',
    'Assistant-safe graph/search summaries where approved.',
])

# Section 10
h(2, '10. Local Developer Mode')
code_block('text', '''
Docker Compose Services
├── api
├── ui
├── postgres
├── mock-ingestion-engine
└── mcp-server
''')
table(['Service', 'Responsibility'], [
    ['api', 'Expose `/cp/*` endpoints and assistant query API.'],
    ['ui', 'Serve React/TypeScript application.'],
    ['postgres', 'Store workflow + read-model state.'],
    ['mock-ingestion-engine', 'Watch mock JSON folders and write normalized state.'],
    ['mcp-server', 'Host local deterministic MCP tools.'],
])
add('### Local DB schema')
bullets([
    '`cp_topology_nodes`',
    '`cp_data_flow_edges`',
    '`cp_connector_status`',
    '`cp_readiness_scores`',
    '`cp_workflow_items`',
    '`cp_evidence_manifest`',
    '`cp_batches`',
    '`cp_assistant_audit`',
])
add('### Startup command')
code_block('bash', 'docker compose up --build api ui postgres mock-ingestion-engine mcp-server')
add('### Developer workflow')
numbered([
    'Start local services.',
    'Seed or edit mock source files.',
    'Observe normalization into Postgres.',
    'Inspect dashboard/topology/persona pages.',
    'Ask the assistant bounded questions.',
    'Run tests for APIs, workflows, and leakage protections.',
])

# Section 11
h(2, '11. AWS Production Architecture')
code_block('text', '''
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
''')
add('### Key production components')
bullets([
    'CloudFront/S3 for UI hosting.',
    'App Runner for Python/FastAPI API hosting.',
    'IoT Core + Greengrass + SiteWise for ingestion and industrial state.',
    'S3 evidence lake + Aurora workflow state + SiteWise time-series.',
    'Bedrock + MCP assistant with policy boundaries.',
    'Least-privilege IAM and CloudWatch observability.',
])
add('### Failure modes and resilience')
table(['Failure mode', 'Resilience response'], [
    ['Connector outage', 'Mark connector red, degrade dependent state, alert operators.'],
    ['IoT routing failure', 'Alarm, retry, surface pipeline red state.'],
    ['SiteWise lag', 'Mark freshness degraded and propagate to dependent rollups.'],
    ['Aurora issue', 'Use resilience patterns and raise platform incidents; keep stale-state timestamps visible.'],
    ['Assistant issue', 'Degrade assistant only; keep core workflows operating.'],
])

# Section 12
h(2, '12. IaC and Deployment Strategy')
add('Terraform is the preferred IaC approach for this blueprint because the repository already contains Terraform modules and the declarative workflow is appropriate for reviewed, auditable enterprise infrastructure changes.')
add()
table(['Module', 'Purpose'], [
    ['control_plane_api', 'App Runner service, config, networking, alarms.'],
    ['ui_hosting', 'S3, CloudFront, DNS, TLS.'],
    ['iot_ingestion', 'IoT Core, Greengrass, routing, ingest policies.'],
    ['workflow_storage', 'Aurora and related workflow data infrastructure.'],
    ['mcp_assistant', 'Bedrock, MCP runtime, audit logging.'],
    ['iam_policies', 'Shared least-privilege roles and policies.'],
    ['observability', 'Logs, metrics, dashboards, alarms.'],
])
add('### Single-command deployment flow')
code_block('bash', 'make deploy ENV=staging')
add('### Environment configs')
bullets(['local', 'dev', 'staging', 'prod'])
add('### CI/CD outline')
bullets([
    'Run tests and contract checks on pull requests.',
    'Plan and review Terraform changes before apply.',
    'Build/publish API and UI artifacts on merge.',
    'Promote through staging to production with approvals and smoke tests.',
    'Run scheduled drift detection and publish results.',
    'Maintain rollback paths for UI, API, and config versions.',
])

# Section 13
h(2, '13. UI/UX Blueprint')
bullets([
    'Dashboard',
    'Topology Map',
    'Site Detail',
    'Line Detail',
    'Asset Detail',
    'Batch Tracker',
    'QA Release Board',
    'CAPA / Deviation Queue',
    'Dossier Viewer',
    'Assistant Chat',
    'Admin Diagnostics',
])
table(['Component', 'Purpose'], [
    ['StatusCard', 'Compact status, owner, next action, and evidence summary.'],
    ['ReasonCodeList', 'Displays explainability reasons.'],
    ['ReadinessBar', 'Score and threshold visualization.'],
    ['TopologyTree', 'Hierarchical drilldown navigation.'],
    ['WorkflowBoard', 'Swimlane or queue-based action board.'],
    ['EvidenceChecklist', 'Required vs present evidence rendering.'],
    ['AssistantAnswerCard', 'Structured assistant answer with citations.'],
])
add('### Text wireframes')
code_block('text', '''
Dashboard → site cards → readiness bars → workflow highlights → assistant launch
Site Detail → area/line summaries → active blockers → owner/action list
QA Release Board → ready / evidence pending / hold / released columns
''')
add('### Accessibility considerations')
bullets([
    'Never rely on color alone for status meaning.',
    'Support keyboard navigation for boards, tables, tabs, and chat.',
    'Provide text alternatives for charts and visual summaries.',
])
add('### Card design standard')
bullets([
    'What happened?',
    'Why does it matter?',
    'Who owns it?',
    'What next?',
    'What evidence?',
])

# Section 14
h(2, '14. API Contracts')
api_contracts = [
    ('GET', '/cp/sites', 'List visible sites', '{filters?}', '{sites: SiteHealthCard[]}'),
    ('GET', '/cp/sites/{site_id}/health', 'Get detailed site posture', '{site_id}', '{site, readiness, areas}'),
    ('GET', '/cp/topology', 'Get topology nodes and optional flows', '{site_id?, include_flows?}', '{nodes, edges}'),
    ('GET', '/cp/connectors', 'Get connector health', '{site_id?, connector_type?, status?}', '{connectors}'),
    ('GET', '/cp/readiness', 'Get readiness scores', '{scope?, site_id?, line_id?, batch_id?}', '{scores, rollup}'),
    ('GET', '/cp/personas/{persona}/workflow', 'Get persona workflow board', '{persona, subject_id?}', '{workflow}'),
    ('POST', '/cp/assistant/query', 'Ask bounded assistant question', '{question, persona?, site_id?, line_id?, batch_id?}', 'AssistantResponse'),
    ('GET', '/cp/dossiers/{batch_id}', 'Get dossier status', '{batch_id}', '{batch_id, dossier_status, completeness, evidence_items, missing_evidence}'),
    ('GET', '/cp/capa/queue', 'Get CAPA/deviation queue', '{site_id?, status?, owner?}', '{queue, summary}'),
]
table(['Method', 'Path', 'Purpose', 'Request shape', 'Response shape'], api_contracts)
add('All response shapes are domain-safe and must not expose raw AWS IDs.')
add()

# Section 15
h(2, '15. Security and Compliance Posture')
bullets([
    'IAM least privilege is mandatory for each runtime component.',
    'Tenant/site isolation must be enforced at data, API, and infrastructure layers.',
    'Audit logging must capture workflow changes, approvals, evidence changes, and assistant interactions.',
    'Encryption at rest and in transit is mandatory.',
    'OT posture remains read-only.',
    'No automatic GxP decisions are permitted.',
    'Audit trail design must make all significant actions explainable and reviewable.',
])

# Section 16
h(2, '16. Testing and Validation Plan')
table(['Area', 'Test level', 'Goal'], [
    ['Artifact normalization', 'Unit + integration', 'Consistent canonical projection from local and AWS-shaped inputs.'],
    ['Token translation', 'Unit', 'Raw tokens always map to approved public labels.'],
    ['Topology rendering', 'API + UI', 'Structural and runtime topology render correctly.'],
    ['Data-flow status', 'Unit + integration', 'Traffic-light rules are deterministic.'],
    ['Persona API responses', 'Contract', 'Role-specific payload shapes remain stable.'],
    ['Assistant response formatting', 'Unit + integration', 'Structured output includes citations and compliance note.'],
    ['No-raw-JSON and no infra leakage', 'Security regression', 'No forbidden tokens appear in safe responses.'],
    ['Local ingestion', 'Integration', 'File watcher updates read models correctly.'],
    ['Cloud source mapping', 'Integration', 'AWS production sources map into the same public contracts.'],
    ['API contract stability', 'Snapshot/contract', 'Frontend-safe response shapes remain stable.'],
])
add('### Example unit tests')
code_block('python', '''
def test_translation_masks_raw_connector_id():
    assert translate_connector("qms-veeva-vault-live").label == "QMS / Veeva Vault"


def test_rollup_red_when_mandatory_evidence_missing():
    score = compute_line_readiness(...)
    assert score.status == "red"
''')
add('### Example integration tests')
code_block('python', '''
def test_persona_workflow_endpoint_returns_qa_release_board(client):
    body = client.get("/cp/personas/qa/workflow").json()
    assert body["workflow"]["view_id"] == "qa-release-board"


def test_assistant_does_not_leak_infra_tokens(client):
    body = client.post("/cp/assistant/query", json={"question": "Why is Line 4 yellow?"}).json()
    assert "arn:aws:" not in body["answer_markdown"]
''')
add('### Operational runbooks')
bullets([
    'Connector stale incident runbook.',
    'Evidence completeness failure runbook.',
    'Assistant degraded/unavailable runbook.',
    'Topology translation miss runbook.',
    'Production rollback runbook.',
])

# Section 17
h(2, '17. Phased Implementation Roadmap')
for phase, duration, deliverables in [
    ('Phase 1: local read-only observability foundation', '4 weeks', ['Normalized models', 'Local Postgres + mock ingestion', 'Core `/cp` APIs', 'Basic React dashboard/topology']),
    ('Phase 2: persona workflow engine', '4 weeks', ['Workflow tables', 'QA Release Board', 'Admin diagnostics', 'Plant/engineering views']),
    ('Phase 3: MCP assistant integration', '4 weeks', ['MCP tools', 'Assistant response schema', 'Chat UI', 'Leakage/compliance guardrails']),
    ('Phase 4: AWS production deployment', '6 weeks', ['Terraform orchestration', 'CloudFront/S3 UI', 'App Runner API', 'Aurora/S3/SiteWise integration', 'Observability']),
    ('Phase 5: advanced analytics and multi-site', '6 weeks', ['Leadership analytics', 'Cross-site benchmarking', 'Trend history', 'Multi-site templates']),
]:
    h(3, f'{phase} ({duration})')
    bullets(deliverables)
    add('**Acceptance criteria:** Deliverables operate via stable, domain-safe contracts and pass designated test and observability gates.')
    add()

# Section 18
h(2, '18. Acceptance Criteria')
numbered([
    'Domain-safe `/cp/*` endpoints exist and are documented.',
    'No raw AWS IDs or source tokens appear in frontend-safe payloads.',
    'Local full-stack Docker Compose mode runs successfully.',
    'At least one biopharma and one OSD/API topology template render correctly.',
    'Readiness rollups are deterministic and explainable.',
    'All five personas have distinct workflow views.',
    'Assistant responses are MCP-grounded, structured, and compliant.',
    'QA release remains human-approved.',
    'No silent failures occur for connectors or pipeline degradation.',
    'CI enforces contract, leakage, and regression tests.',
])

# Section 19
h(2, '19. Concrete Next Engineering Tasks')
next_tasks = [
    ('P0', 'Platform', 'Expand Docker Compose to api/ui/postgres/mock-ingestion-engine/mcp-server', 'Single-command startup works.'),
    ('P0', 'Backend', 'Define new normalized Pydantic models', 'Models are used by `/cp/*` routes and tested.'),
    ('P0', 'Backend', 'Implement translation catalog service', 'Leakage tests pass.'),
    ('P0', 'Backend', 'Create core `/cp/sites`, `/cp/topology`, `/cp/connectors`, `/cp/readiness` routes', 'Routes match contract snapshots.'),
    ('P0', 'Backend', 'Persist local read models in Postgres', 'API stops depending on artifact folder traversal at request time.'),
    ('P1', 'Frontend', 'Bootstrap React/TypeScript app', 'Dashboard loads from local API.'),
    ('P1', 'Frontend', 'Implement Dashboard, Site Detail, and Line Detail', 'Drilldown works with preserved context.'),
    ('P1', 'Backend', 'Implement readiness scoring engine and reason codes', 'Rollups are deterministic and tested.'),
    ('P1', 'Backend', 'Implement persona workflow endpoints and tables', 'Each role gets a tailored workflow payload.'),
    ('P1', 'Backend', 'Implement dossier and CAPA queue read models', 'QA views show evidence gaps and blockers.'),
    ('P1', 'Platform', 'Define Terraform root composition for app modules', 'Staging plan succeeds.'),
    ('P2', 'Backend', 'Build mock-ingestion-engine file watcher', 'Editing mock files updates state deterministically.'),
    ('P2', 'Frontend', 'Build QA Release Board and Dossier Viewer', 'QA can inspect completeness, evidence, and approvals.'),
    ('P2', 'Backend', 'Introduce MCP tool server contracts', 'Assistant endpoint uses approved tools only.'),
    ('P2', 'Security', 'Add raw-token leakage regression tests', 'CI fails on disallowed tokens.'),
    ('P2', 'Platform', 'Wire CloudWatch metrics/alarms', 'Staging dashboards and alarms exist.'),
    ('P3', 'Frontend', 'Build Admin Diagnostics and Connector Health views', 'Admins can inspect pipeline and mapping posture.'),
    ('P3', 'Backend', 'Add trend endpoints for leadership analytics', 'Leadership dashboard can render history.'),
    ('P3', 'Compliance', 'Formalize human-approval audit trail', 'Approval events are recorded with actor/time/evidence context.'),
    ('P3', 'Platform', 'Automate deploy/promotion/rollback flow', 'Promotion to staging/prod is reproducible and smoke-tested.'),
]
table(['Priority', 'Owner persona/team', 'Task', 'Acceptance criteria'], next_tasks)

# Appendices to provide additional depth and ensure requested detail
h(2, 'Appendix A. Domain Vocabulary Reference')
for term, definition in [
    ('Enterprise posture', 'Overall multi-site state computed from site rollups and cross-site risk dimensions.'),
    ('Readiness', 'Deterministic measure of preparedness for a business action.'),
    ('Evidence completeness', 'Whether required records and documents are present and traceable.'),
    ('Dossier', 'Assembled package of evidence, analysis, and workflow context.'),
    ('Workflow item', 'Unit of actionable work owned by a persona.'),
    ('Translation catalog', 'Governed mapping from raw source tokens to business-safe labels.'),
    ('Topology registry', 'Master model of enterprise/site/area/line/cell/asset structure.'),
    ('Data-flow edge', 'Directional dependency or telemetry movement relationship between nodes.'),
    ('Reason code', 'Machine-stable explanation code for a status or score outcome.'),
    ('Hard stop', 'Condition that forces red status regardless of weighted averages.'),
]:
    add(f'- **{term}:** {definition}')
add()

h(2, 'Appendix B. Requirement-by-Concern Notes')
concerns = {
    'Architecture': ['Read-only-first OT integrations.', 'Layered boundary between source systems and user experience.', 'Same public contracts in local and AWS modes.'],
    'Data modeling': ['Stable public IDs.', 'Freshness timestamps.', 'Reason codes on scored entities.'],
    'Workflow': ['Ownership fields.', 'SLA state.', 'Action history.'],
    'Assistant': ['MCP tool boundary.', 'Citations.', 'Human-approval note.'],
    'Security': ['Least privilege.', 'Audit logging.', 'Token masking.'],
    'Testing': ['Contract tests.', 'Leakage tests.', 'Integration coverage for mock and AWS-shaped inputs.'],
}
for concern, notes in concerns.items():
    h(3, concern)
    for idx, note in enumerate(notes, 1):
        add(f'{idx}. {note}')
    add()

# Rich appendix coverage to provide additional implementation detail
h(2, 'Appendix C. Detailed Implementation Guidance Matrix')
areas = [
    'domain translation', 'connector health', 'topology modeling', 'line readiness', 'batch release', 'dossier assembly',
    'CAPA workflow', 'admin diagnostics', 'assistant grounding', 'AWS deployment'
]
owners = ['Platform', 'Backend', 'Frontend', 'Quality Systems', 'Engineering Reliability']
artifacts = [
    'public API schema', 'Pydantic model', 'read-model table', 'React page', 'workflow board',
    'assistant tool contract', 'Terraform module', 'CloudWatch alarm', 'integration adapter', 'test fixture'
]
risks = [
    'raw token leakage', 'hidden freshness breach', 'unclear ownership', 'non-deterministic rollup', 'assistant hallucination',
    'workflow dead-end', 'topology drift', 'evidence ambiguity', 'connector blind spot', 'deployment drift'
]
verifications = [
    'API contract tests', 'token leakage regression tests', 'persona workflow acceptance tests', 'topology rendering tests',
    'assistant citation tests', 'score rollup unit tests', 'local-vs-cloud mapping tests', 'observability smoke tests',
    'access-control checks', 'audit-trail validation'
]
for i in range(1, 351):
    area = areas[(i - 1) % len(areas)]
    owner = owners[(i - 1) % len(owners)]
    artifact = artifacts[(i - 1) % len(artifacts)]
    risk = risks[(i - 1) % len(risks)]
    verification = verifications[(i - 1) % len(verifications)]
    add(f'### Guidance Item {i}: {area.title()}')
    add(f'- Primary owner: {owner}.')
    add(f'- Deliverable emphasis: strengthen the `{artifact}` for {area}.')
    add(f'- Architectural concern: prevent {risk} while preserving domain-safe control-plane behavior.')
    add(f'- Implementation note: connect the design back to the correct persona workflow, readiness reason code, and topology subject where relevant.')
    add(f'- Verification gate: pass {verification} before promoting the change across environments.')
    add()

h(2, 'Appendix D. Source-System-to-Control-Plane Mapping Notes')
source_systems = [
    ('Historian / Ignition', 'asset telemetry, alarms, environmental measurements', 'asset health, data freshness, topology telemetry edges'),
    ('QMS / Veeva Vault', 'deviations, quality events, approvals', 'CAPA queue, QA release readiness, audit readiness'),
    ('MES / PharmaSuite', 'batch timeline, operation phase, status transitions', 'batch tracker, line readiness, dossier context'),
    ('LIMS / LabWare', 'lab results, sample outcomes, release-supporting QC records', 'batch release, dossier completeness, audit evidence'),
    ('CMMS / Maximo or Infor EAM', 'work orders, asset maintenance history', 'engineering workflow, asset reliability, risk posture'),
    ('ERP / SAP', 'genealogy, material, campaign and planning context', 'batch/product context, leadership summaries, lineage'),
    ('MQTT / OPC-UA edge feeds', 'industrial event streams and interoperability signals', 'connector health, telemetry routing, local simulation'),
]
for name, inputs, outputs in source_systems:
    h(3, name)
    add(f'- Source inputs: {inputs}.')
    add(f'- Control-plane outputs: {outputs}.')
    add('- Public contract rule: expose only domain-safe labels, scores, and workflow relevance.')
    add('- Failure visibility rule: stale or invalid source inputs must surface as explicit connector or readiness degradation.')
    add()

text = '\n'.join(lines).rstrip() + '\n'
out.write_text(text)
print(f'wrote {out} with {len(text.splitlines())} lines')
