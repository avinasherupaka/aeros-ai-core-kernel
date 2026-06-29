# Mission-Critical Target Architecture

Areos.ai = **Assurance, Reliability, Efficiency Operating System**.

## Core positioning

- Areos is a **system of assurance, not a system of record**.
- **Do not sell monitoring; sell proof.**
- Existing systems monitor signals; Areos connects signals to validated state, product impact, and audit evidence.
- Primary lineage: **Utility event → area → batch/product/material → quality risk → evidence → decision.**
- Areos does **not** replace MES, QMS, BMS, EMS, SCADA, historians, CMMS, LIMS, ERP, OEE, or lakehouse platforms.
- Areos orchestrates evidence across those systems so regulated decisions can be supported by deterministic, auditable facts.

## Runtime stance

- **AWS-native tenant-site cell** is the intended runtime architecture.
- The **local sandbox** in this repository is a developer and test harness only.
- **AWS Greengrass V2 only** is the supported edge runtime pattern for site connectivity and OT-adjacent integration.

## Architectural objective

The target system must turn fragmented industrial and quality records into defensible assurance outputs:

1. detect and normalize operational events
2. bind events to site, area, equipment, batch, product, and material context
3. determine state and impact through deterministic algorithms
4. assemble evidence and provenance
5. route structured conclusions to human reviewers
6. render explanations without changing deterministic truth

## What the architecture must guarantee

### 1. Deterministic regulated conclusions
Regulated conclusions must come from versioned, deterministic algorithms. The same input plus the same rule, schema, and code versions must reproduce the same output.

### 2. Idempotent ingestion and processing
Source events must be fingerprinted canonically so replay, retry, and connector reprocessing do not create duplicate regulated artifacts.

### 3. Evidence lineage and provenance
Every answer, dossier section, and workflow object must preserve source citations and transformation lineage so auditors can trace the factual basis of a conclusion.

### 4. Human-governed GxP decisions
Areos may prioritize, summarize, and draft, but it must not autonomously release product, close deviations, or claim automatic compliance.

### 5. Read-only-first industrial integration
OT integrations must be read-only by default. The platform is designed to observe and prove, not to control plant equipment.

## Major runtime domains

### Site edge domain
- Greengrass V2 core device
- read-only connectors to OT and operational sources
- local buffering and replay for intermittent connectivity
- normalization into a canonical event envelope before cloud publishing

### AWS ingestion domain
- Amazon IoT Core and IoT Rules for industrial telemetry/event ingress
- EventBridge for enterprise event routing
- SQS and DLQ patterns for resilient decoupling
- AWS IoT SiteWise for industrial asset models and hot/warm time-series

### Enterprise data backbone
- S3 lakehouse with Apache Iceberg-style table contracts
- Glue Data Catalog + Lake Formation governance
- Neptune evidence/provenance graph
- DynamoDB or Aurora PostgreSQL for workflow state and idempotency
- OpenSearch / Bedrock Knowledge Bases for retrieval, not regulated truth

### Assurance and workflow domain
- deterministic state-of-control logic
- deterministic event-to-impact mapping
- recurrence/reliability classification
- evidence packaging and audit-readiness services
- deviation, APQR, validation, and plant-head workflow views

### Narrative and experience domain
- Amazon Bedrock provides controlled narrative rendering only
- Bedrock may explain deterministic answers, summarize evidence, and draft human-review text
- Bedrock must not change the factual basis or produce autonomous regulated conclusions

## Compliance language

The platform is **designed to support 21 CFR Part 11 / GxP controls, validation evidence, auditability, electronic-record integrity, and customer CSV**. It does **not** claim automatic compliance, automatic validation, or autonomous approval authority.

## Why this architecture matters

Traditional monitoring stacks show abnormal signals. Areos must prove operational meaning:

- what happened
- where it happened
- what batch, product, or material was exposed
- what quality risk is plausible
- what evidence exists or is missing
- what human decision is now required

That is the mission-critical target architecture: not another dashboard, but a reproducible assurance operating layer on top of existing systems.
