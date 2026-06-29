# Deterministic Algorithmic Engine

## Why this engine exists

Areos must not rely on probabilistic language generation for regulated conclusions. The deterministic algorithmic engine exists so the platform can prove that the same governed input and governed rule set produce the same governed output.

## Core rule

**Bedrock is not the decision engine. Deterministic algorithms produce regulated conclusions.**

## Deterministic processing commitments

- canonical input normalization
- stable event fingerprinting
- idempotent replay behavior
- versioned rule/schema/code context
- structured outputs with citations and missing-evidence reporting
- human review requirement for GxP decisions

## Processing chain

### 1. Canonicalization
Source events are normalized into a shared schema so different connector payloads can be evaluated consistently.

### 2. Fingerprinting
A canonical SHA-256 fingerprint is computed over tenant, site, source identity, source timestamp, parameter, value, unit, and schema version. Same input in any key order yields the same fingerprint.

### 3. Idempotency
The fingerprint is checked against a registry. Replays, retries, and duplicate webhook deliveries should not generate duplicate regulated outputs.

### 4. Versioned rule evaluation
Processing occurs under explicit versions for:
- kernel code
- schema
- ontology
- each deterministic rule family

### 5. Structured answer generation
Outputs are represented as deterministic answer objects containing:
- answer type
- decision state
- basis facts
- citations
- missing evidence
- generated version context

## Key algorithm families

### State of control
Determines whether an operational condition was in control, out of control, or pending review based on validated limits and observed evidence.

### Event to impact
Links an event to area, room, batch, product, and material exposure and translates signal deviation into quality-relevant impact hypotheses.

### Reliability / recurrence
Determines whether an event is isolated or recurring and provides deterministic classification for engineering follow-up.

### Evidence packaging
Builds auditable manifests and missing-evidence checklists from governed source inputs.

### APQR assembly
Produces structured annual product quality review sections from deterministic event and evidence products.

## What the engine must never do

- invent source evidence
- release a batch autonomously
- close a deviation autonomously
- claim automatic 21 CFR Part 11 compliance
- issue OT write/control commands as part of assurance reasoning

## Human governance model

The engine can confirm deterministic findings such as a validated excursion or an incomplete evidence package, but any GxP decision still requires human review and approval.

## Compliance language

The deterministic engine is **designed to support 21 CFR Part 11 / GxP controls, validation evidence, auditability, electronic-record integrity, and customer CSV**. Customer validation and procedural controls remain required.
