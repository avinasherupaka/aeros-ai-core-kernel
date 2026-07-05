# Enterprise Control Plane — Implementation Backlog

This backlog prioritizes the local-first enterprise control plane, the normalized readiness model, persona-driven workflows, and the MCP assistant layer needed for regulated manufacturing environments. Priorities assume one shared platform team with parallel frontend and cloud enablement workstreams.

## Sprint 0 — Foundation (Week 1-2)

| ID | Title | Priority | Story Points | Acceptance Criteria | Dependencies |
| --- | --- | --- | ---: | --- | --- |
| CP-001 | Domain abstraction token translation engine | Critical | 8 | Canonical translation service maps infrastructure/source identifiers to domain-safe labels with deterministic lookup tests and admin override support. | None |
| CP-002 | Infrastructure masking layer — no raw IDs in primary UI responses | Critical | 5 | Non-admin API serializers redact or translate raw ARNs, connector IDs, asset GUIDs, and internal record keys before response emission. | CP-001 |
| CP-003 | Normalized ControlPlaneSnapshot API endpoint | Critical | 8 | `/control-plane/api/overview` returns a stable, versioned normalized snapshot contract with topology, readiness, and connector summaries. | CP-001, CP-002 |
| CP-004 | SiteHealthCard model and endpoint | High | 5 | Site health endpoint returns site label, traffic-light status, top reasons, and timestamp with contract tests. | CP-003 |
| CP-005 | ConnectorStatusCard with domain labels only | High | 5 | Connector status payload shows business-facing labels, direction, SLA state, and evidence timestamp without leaking implementation identifiers. | CP-001, CP-002, CP-003 |
| CP-006 | Local Docker Compose control plane stack | High | 3 | Separate compose file boots API, Postgres, ingestion, MQTT, MCP, and optional UI profiles with documented ports and health checks. | None |
| CP-007 | PostgreSQL schema for workflow state | High | 8 | Alembic-ready schema covers workflow state, readiness snapshots, connector state, and audit timestamps with migration smoke test. | CP-003 |
| CP-008 | Mock ingestion file watcher service | Medium | 3 | Local watcher detects artifact changes, writes normalized cache output, and runs in local mock mode without AWS credentials. | CP-006 |

## Sprint 1 — Readiness Engine (Week 3-4)

| ID | Title | Priority | Story Points | Acceptance Criteria | Dependencies |
| --- | --- | --- | ---: | --- | --- |
| CP-009 | Traffic-light readiness score engine | Critical | 8 | Readiness engine computes red/amber/green with configurable thresholds across data, quality, process, and infrastructure dimensions. | CP-003, CP-007 |
| CP-010 | Hierarchical rollup asset→line→area→site→enterprise | Critical | 8 | Rollup service propagates leaf readiness to each hierarchy level using documented aggregation rules and traceable evidence lineage. | CP-009 |
| CP-011 | Reason codes and recommended actions per dimension | High | 5 | Every non-green or degraded state includes at least one reason code and recommended action bundle. | CP-009 |
| CP-012 | SLA configuration model | High | 5 | SLA model stores target freshness, availability, and latency thresholds by connector and process domain. | CP-007 |
| CP-013 | No-silent-failures rule enforcement | Critical | 5 | Missing or stale data can never resolve to green; engine explicitly emits missing-data evidence and degraded readiness. | CP-009, CP-012 |
| CP-014 | ReadinessScore unit tests | High | 5 | Unit test suite covers scoring thresholds, stale data, missing data, rollups, and edge cases with deterministic fixtures. | CP-009, CP-010, CP-013 |
| CP-015 | Connector SLA breach detection | High | 5 | Control plane flags SLA breaches with severity, elapsed breach duration, and impacted scope. | CP-012, CP-013 |
| CP-051 | Readiness API contract and fixture pack | High | 3 | Versioned JSON fixtures validate readiness contracts for asset, site, and enterprise views in local mock mode. | CP-009, CP-010, CP-014 |

## Sprint 2 — Persona Workflows (Week 5-6)

| ID | Title | Priority | Story Points | Acceptance Criteria | Dependencies |
| --- | --- | --- | ---: | --- | --- |
| CP-016 | System Administrator workflow endpoint | High | 5 | Admin workflow endpoint returns connector health, stale feeds, alert counts, and drill-down actions with admin-only fields gated. | CP-003, CP-015 |
| CP-017 | QA Release Board endpoint | Critical | 8 | QA release board presents release blockers, affected batches, evidence references, and mandatory human approval status. | CP-009, CP-011 |
| CP-018 | Plant Ops risk heatmap endpoint | High | 5 | Plant Ops workflow returns area/line heatmap data, bottleneck reasons, and recommended operating actions. | CP-010, CP-011 |
| CP-019 | Engineering Reliability Board endpoint | High | 5 | Reliability endpoint highlights recurring failure modes, connector trends, and maintenance-linked risk drivers. | CP-010, CP-015 |
| CP-020 | Leadership executive summary endpoint | High | 5 | Executive summary shows enterprise readiness, top risks, and site comparison tiles with masked infrastructure detail. | CP-010, CP-021 |
| CP-021 | Role-based API response filtering | Critical | 8 | Persona-aware response filter enforces field-level visibility rules and denies raw technical detail outside admin audiences. | CP-002, CP-003 |
| CP-022 | Persona-specific KPI definitions | Medium | 3 | KPI registry defines metrics, labels, thresholds, and tooltips per persona with documentation and fixtures. | CP-016, CP-017, CP-018, CP-019, CP-020 |
| CP-052 | Workflow audit trail envelope | High | 5 | All persona endpoints return correlation ID, evidence timestamp, and response version metadata for auditability. | CP-017, CP-021 |

## Sprint 3 — MCP Assistant (Week 7-8)

| ID | Title | Priority | Story Points | Acceptance Criteria | Dependencies |
| --- | --- | --- | ---: | --- | --- |
| CP-023 | MCP server tool registry | Critical | 5 | MCP registry exposes approved tools, schemas, persona scoping, and audit metadata in a deterministic catalog. | CP-021 |
| CP-024 | get_site_status tool implementation | Critical | 5 | Assistant tool returns normalized site status, top blockers, and evidence citations for a requested site. | CP-003, CP-023 |
| CP-025 | get_line_readiness tool implementation | High | 5 | Tool returns line-level readiness, degraded dimensions, and recommended actions using domain labels only. | CP-009, CP-010, CP-023 |
| CP-026 | get_batch_release_status tool | Critical | 8 | Tool reports batch release readiness, blockers, and explicit GxP human-approval requirement before decision closure. | CP-017, CP-023 |
| CP-027 | AssistantResponse format enforcement — no raw JSON output | Critical | 5 | Assistant renderer wraps all tool results into structured prose/cards and rejects raw JSON-only responses. | CP-023, CP-024, CP-025 |
| CP-028 | No-infrastructure-token leakage test in assistant | Critical | 5 | Automated tests assert assistant responses never leak ARNs, GUIDs, connector IDs, or raw schema internals. | CP-002, CP-027 |
| CP-029 | Grounding strategy on normalized control plane data | High | 5 | Assistant retrieval layer grounds only on normalized control plane snapshots, readiness summaries, and approved evidence packs. | CP-003, CP-027 |
| CP-030 | Good/prohibited response examples test suite | High | 3 | Golden examples verify compliant phrasing, evidence citation, GxP escalation behavior, and prohibited response rejection. | CP-027, CP-028, CP-029 |

## Sprint 4 — AWS Production (Week 9-12)

| ID | Title | Priority | Story Points | Acceptance Criteria | Dependencies |
| --- | --- | --- | ---: | --- | --- |
| CP-031 | App Runner Terraform module for API | High | 5 | Terraform module provisions API service, scaling, health checks, IAM access role, and environment variables. | CP-003 |
| CP-032 | CloudFront + S3 Terraform module for UI | High | 5 | Terraform module provisions private S3 origin, CloudFront distribution, HTTPS redirect, and origin access control. | CP-020 |
| CP-033 | MCP Lambda Terraform module | High | 5 | Terraform module provisions Lambda, IAM read-only access, and API Gateway invoke permissions for assistant runtime. | CP-023 |
| CP-034 | Aurora Serverless for workflow state | High | 8 | Production workflow state store deployed with automated backups, encryption, and connection settings for control plane services. | CP-007 |
| CP-035 | IAM least-privilege policy scaffold | Critical | 8 | Shared IAM policy library limits service permissions to required resources, actions, and environments with review checklist. | CP-031, CP-033, CP-034 |
| CP-036 | CloudWatch structured logging | High | 5 | API, Lambda, and ingestion runtimes emit structured logs with correlation IDs, readiness context, and alert-friendly fields. | CP-031, CP-033 |
| CP-037 | Environment config: local/dev/staging/prod | High | 5 | Environment overlays define ports, feature flags, endpoints, and secrets references consistently across deploy targets. | CP-031, CP-032, CP-033 |
| CP-038 | Single-command deploy script | Medium | 3 | One documented command plans/applies infrastructure and publishes required build artifacts per environment. | CP-031, CP-032, CP-033, CP-037 |
| CP-039 | Bedrock Knowledge Base integration | Medium | 5 | Assistant infrastructure supports knowledge base ID wiring, retrieval permissions, and environment-safe toggles. | CP-033 |
| CP-040 | Tenant/site isolation enforcement | Critical | 8 | Runtime and data access controls enforce tenant/site boundaries in API, database, storage, and assistant retrieval flows. | CP-021, CP-034, CP-035 |

## Sprint 5 — Frontend React UI (Week 9-12, parallel)

| ID | Title | Priority | Story Points | Acceptance Criteria | Dependencies |
| --- | --- | --- | ---: | --- | --- |
| CP-041 | React app scaffold with TypeScript | High | 5 | Frontend workspace includes React, TypeScript, Vite, environment config, and local mock API wiring. | CP-006 |
| CP-042 | TrafficLightBadge component | High | 3 | Shared component renders red/amber/green states accessibly with icon, label, and tooltip support. | CP-041 |
| CP-043 | SiteHealthCard component | High | 5 | Card renders site readiness, reasons, evidence timestamp, and escalation CTA from normalized API data. | CP-004, CP-041 |
| CP-044 | ConnectorStatusCard component | High | 5 | Card renders connector status, SLA breach state, direction, and domain-safe labels only. | CP-005, CP-041 |
| CP-045 | TopologyMap component | High | 8 | Topology visualization shows enterprise/site/area/line relationships, rollup colors, and drill-down interactions. | CP-003, CP-010, CP-041 |
| CP-046 | PersonaTabBar and navigation | High | 3 | UI supports persona switching, route guards, and consistent navigation across workflow views. | CP-041, CP-021 |
| CP-047 | AssistantPanel component | High | 5 | Assistant panel renders cited answers, action prompts, and prohibited-output guardrails in the control plane shell. | CP-027, CP-029, CP-041 |
| CP-048 | DossierViewer page | High | 5 | Dossier page displays evidence sections, manifests, and export affordances from normalized API contracts. | CP-003, CP-041 |
| CP-049 | QA Release Board page | Critical | 8 | Release board page visualizes release blockers, batch status, evidence links, and human approval requirement banners. | CP-017, CP-043, CP-047 |
| CP-050 | Admin Diagnostics drawer | Medium | 5 | Admin-only diagnostics panel exposes technical status, stale feed details, and audit metadata without leaking into non-admin views. | CP-016, CP-021, CP-044 |

## Acceptance Criteria — System-Wide

1. No raw AWS ARNs, connector IDs, or internal identifiers appear in any non-admin API response.
2. All connector statuses are shown with domain labels and business-facing descriptions.
3. Assistant never outputs raw JSON or schema dumps to end users.
4. Assistant always cites at least one evidence source for readiness or release-status claims.
5. Every readiness status includes at least one reason code.
6. Missing, stale, or partial data can never silently resolve to green.
7. Hierarchical rollups match documented leaf-node aggregation rules and are reproducible from fixtures.
8. GxP release decisions are always deferred to explicit human approval steps.
9. Local mock mode runs all API and assistant tests without AWS credentials.
10. Docker Compose control plane boots with deterministic local dependencies and documented ports.
11. PostgreSQL workflow schema supports audit timestamps, correlation IDs, and soft evolution through migrations.
12. Persona filtering prevents admin-only diagnostic fields from appearing in QA, Ops, or leadership responses.
13. MCP tool contracts expose only approved, normalized data fields.
14. Control plane API contracts are versioned and validated by integration tests.
15. Cloud deployment modules tag all resources with application and environment metadata.
16. IAM policies for production services are least-privilege and reviewed before release.
17. CloudFront UI hosting serves over HTTPS and does not require public S3 bucket access.
18. Lambda assistant runtime has read-only access to DynamoDB and S3 knowledge sources.
19. Structured logs include correlation IDs for API, ingestion, and assistant interactions.
20. Tenant/site isolation rules are enforced in persistence, retrieval, and response rendering paths.

## Definition of Done

- Code reviewed
- Unit tests ≥ 80% coverage on new code
- Integration test validates API contract
- No infrastructure token leakage in test assertions
- Documentation updated
- Security and IAM review completed for cloud-facing changes
- Local mock mode demo executed successfully for affected workflows
