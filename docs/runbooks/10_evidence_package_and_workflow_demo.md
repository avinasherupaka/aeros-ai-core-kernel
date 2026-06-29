# 10 Evidence Package and Workflow Demo

This runbook covers the **hardened Phase 3–5 product behavior** introduced in the functional hardening pass. It uses the local sandbox/test harness only — no AWS credentials required. The AWS-native tenant-site cell runtime remains the production target.

## What was previously scaffolded / what this PR hardened

| Area | Before | After |
|------|--------|-------|
| GMP dossier | `dossier.md` + `dossier.json` only | Full 8-file evidence package with manifest, evidence index, source citations, missing-evidence checklist, approval placeholder, SHA-256 hashes, completeness score |
| State-of-control | Basic breach/alert/severity | + Confidence breakdown (source quality, completeness, time-window continuity, context), first/last breach timestamps, longest continuous breach window, evidence references |
| Event-to-impact | Lists of risks and evidence | + ImpactRationale per entity, ImpactPath (event→area→equipment→batch→risk→evidence→decision), risk severity scores, decision options, per-item evidence status |
| Reliability intelligence | Simple recurrence count + classification | + Similarity scoring, recommended engineering actions per classification, recurrence grouped by asset::metric |
| Evidence graph | Nodes + edges snapshot | + Query/traversal methods on InMemoryEvidenceGraph and EvidenceGraphQuery; `to_neptune_like_triples()` for future Neptune mapping |
| APQR/PQR builder | Short summary object | + Event table, excursion trends, risk themes, CAPA effectiveness, open evidence gaps, human review statement, Markdown + JSON file output |
| Deviation workbench | Queue only | + `create_deviation_draft()` returning structured draft with containment actions |
| Engineering reliability board | Counts + topics | + Suggested engineering actions from reliability insights, maintenance effectiveness flags, asset recurrence table |
| Plant head assurance | Event lists | + Site risk score, risk tier (low/medium/high/critical), plain-language executive summary |
| Validation/audit control room | Completeness dict | + Dossier completeness table, audit-ready/not-audit-ready status per event |
| API endpoints | 10 endpoints | + 6 new: `/full-package`, `/generate-package`, `/manifest`, `/apqr/{site_id}/demo-section`, `/apqr/{site_id}/generate-demo-section`, `/workflows/deviation-drafts/{event_id}` |

---

## 1. Install and run tests

```bash
cd /path/to/aeros-ai-core-kernel
python -m pip install -e '.[dev]'
pytest -q
# Expected: 89 passed
```

Run only the new hardened tests:

```bash
pytest -q tests/test_state_of_control_hardened.py \
          tests/test_event_to_impact_hardened.py \
          tests/test_reliability_hardened.py \
          tests/test_evidence_graph_hardened.py \
          tests/test_dossier_full_package.py \
          tests/test_apqr_hardened.py \
          tests/test_workflow_hardened.py
```

---

## 2. Generate a full GMP evidence package

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.dossiers.gmp_dossier import build_gmp_dossier

bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
dossier = build_gmp_dossier(
    event=bundle.event,
    assessment=bundle.assessment,
    impact_assessment=bundle.impact,
    evidence_graph=bundle.evidence_graph,
    reliability_insight=bundle.reliability_insight,
)
print("Package completeness score:", dossier.package_completeness_score)
print("Manifest path:", dossier.manifest_path)
print("Approval placeholder:", dossier.approval_placeholder_path)
print("Package hashes:", dossier.package_hashes_path)
PY
```

### Inspect the generated files

```bash
# List all files in the generated package
ls artifacts/evidence/*/*/events/event__pharma_osd_humidity_excursion_compression/

# View the manifest
cat artifacts/evidence/*/*/events/event__pharma_osd_humidity_excursion_compression/manifest.json | python3 -m json.tool

# View the evidence index (shows present/missing per item)
cat artifacts/evidence/*/*/events/event__pharma_osd_humidity_excursion_compression/evidence_index.json | python3 -m json.tool

# View source citations table
cat artifacts/evidence/*/*/events/event__pharma_osd_humidity_excursion_compression/source_citations.json | python3 -m json.tool

# View the approval placeholder with e-signature fields
cat artifacts/evidence/*/*/events/event__pharma_osd_humidity_excursion_compression/approval_placeholder.json | python3 -m json.tool

# Verify SHA-256 package integrity hashes
cat artifacts/evidence/*/*/events/event__pharma_osd_humidity_excursion_compression/package_hashes.json | python3 -m json.tool
```

---

## 3. Inspect state-of-control confidence breakdown

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from pprint import pprint

bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
a = bundle.assessment
print("Outcome:", a.outcome.value)
print("Severity:", a.severity)
print("Confidence:", a.confidence)
print("Confidence explanation:", a.confidence_explanation)
print("Confidence breakdown:")
pprint(a.confidence_breakdown)
print("Breach start:", a.breach_start)
print("Breach end:", a.breach_end)
print("Parameter assessments (first):")
if a.parameter_assessments:
    p = a.parameter_assessments[0]
    print("  first_breach_timestamp:", p.get("first_breach_timestamp"))
    print("  last_breach_timestamp:", p.get("last_breach_timestamp"))
    print("  longest_continuous_breach_minutes:", p.get("longest_continuous_breach_minutes"))
    print("  evidence_references:", p.get("evidence_references"))
PY
```

---

## 4. Inspect event-to-impact with rationale, path, and decision options

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.assurance.event_to_impact import evaluate_event_impact
from aeros.kernel.ontology.industry_packs import build_demo_ontology_context, get_scenario_definition
from pprint import pprint

bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
impact = evaluate_event_impact(
    bundle.event,
    build_demo_ontology_context(bundle.scenario_id),
    get_scenario_definition(bundle.scenario_id),
)
print("Decision options:")
pprint(impact.decision_options)
print("Impact path:", impact.impact_path.path_steps if impact.impact_path else None)
print("Risk severity scores:")
pprint(impact.risk_severity_scores)
print("Evidence status list:")
for item in impact.evidence_status_list:
    print(f"  [{item.status}] {item.evidence_item}")
print("Impact rationale (first):", impact.impact_rationale[0] if impact.impact_rationale else None)
PY
```

---

## 5. Query the evidence graph

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.assurance.evidence_graph import query_snapshot

bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
q = query_snapshot(bundle.evidence_graph)
event_id = bundle.event.event_id

print("Evidence items:")
for node in q.get_event_evidence(event_id):
    print(f"  [{node.node_type.value}] {node.label}")

print("\nImpacted entities:")
for node in q.get_impacted_entities(event_id):
    print(f"  [{node.node_type.value}] {node.label}")

print("\nRisks:")
for node in q.get_risks(event_id):
    print(f"  [{node.node_type.value}] {node.label}")

print("\nLineage path:")
for step in q.get_lineage_path(event_id):
    print(f"  {step}")

print("\nNeptune-like triples (first 5):")
for triple in q.to_neptune_like_triples()[:5]:
    print(f"  {triple['subject_type']}:{triple['subject']} --[{triple['predicate']}]--> {triple['object_type']}:{triple['object']}")
PY
```

---

## 6. Reliability intelligence — recommended engineering actions

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from pprint import pprint

bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
r = bundle.reliability_insight
print("Classification:", r.classification.value)
print("Similarity score:", r.similarity_score)
print("Recurrence by asset::metric:", r.recurrence_by_asset_metric)
print("Recommended engineering actions:")
pprint(r.recommended_engineering_actions)
PY
```

---

## 7. Generate APQR/PQR section with file output

```bash
python - <<'PY'
import tempfile
from aeros.kernel.api.demo_data import demo_event_bundles
from aeros.kernel.dossiers.apqr import build_apqr_section

bundles = list(demo_event_bundles().values())
events = [b.event for b in bundles]
impacts = [b.impact for b in bundles]
insights = [b.reliability_insight for b in bundles]

with tempfile.TemporaryDirectory() as tmp:
    section = build_apqr_section(
        site_id="enterprise_demo",
        events=events,
        impacts=impacts,
        reliability_insights=insights,
        period="2026-H1",
        output_root=tmp,
    )
    print("APQR period:", section.period)
    print("Event table count:", len(section.event_table))
    print("Risk themes:", section.risk_themes[:3])
    print("Open evidence gaps (first 3):", section.open_evidence_gaps[:3])
    print("Human review statement:", section.human_review_statement)
    print("Markdown path:", section.markdown_path)
    print("JSON path:", section.json_path)
PY
```

---

## 8. Workflow services — deviation draft, risk score, audit-ready status

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.workflows.deviation_workbench import create_deviation_draft, build_deviation_queue
from aeros.kernel.workflows.engineering_reliability_board import build_engineering_reliability_board
from aeros.kernel.workflows.plant_head_assurance import build_plant_head_assurance_view
from aeros.kernel.workflows.validation_audit_room import build_validation_audit_room

bundles = [
    get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression"),
    get_demo_event_bundle("event::api_reactor_temperature_excursion"),
]
events = [b.event for b in bundles]
impacts = [b.impact for b in bundles]
insights = [b.reliability_insight for b in bundles]
dossiers = [b.dossier for b in bundles]

# Deviation draft
draft = create_deviation_draft(bundles[0].event, bundles[0].impact, bundles[0].dossier)
print("=== Deviation Draft ===")
print("Title:", draft.deviation_title)
print("Problem statement:", draft.problem_statement)
print("Containment actions:", draft.suggested_immediate_containment)
print("Human approval required:", draft.human_approval_required)

# Deviation queue with due_status
queue = build_deviation_queue(events, impacts)
print("\n=== Deviation Queue ===")
for item in queue.queue:
    print(f"  [{item.due_status}] {item.event_id} (severity: {item.severity})")

# Engineering reliability board
board = build_engineering_reliability_board(site_id="enterprise_demo", events=events, reliability_insights=insights)
print("\n=== Engineering Reliability Board ===")
print("Asset recurrence table:", board.asset_recurrence_table)
print("Suggested engineering actions:", board.suggested_engineering_actions[:2])
print("Maintenance effectiveness flags:", board.maintenance_effectiveness_flags)

# Plant head assurance
plant = build_plant_head_assurance_view(site_id="enterprise_demo", events=events, impacts=impacts, reliability_insights=insights)
print("\n=== Plant Head Assurance ===")
print("Site risk score:", plant.site_risk_score)
print("Site risk tier:", plant.site_risk_tier)
print("Executive summary:", plant.executive_summary)

# Validation audit room
room = build_validation_audit_room(site_id="enterprise_demo", dossiers=dossiers, impacts=impacts)
print("\n=== Validation/Audit Control Room ===")
print("Dossier completeness table:", room.dossier_completeness_table)
print("Audit-ready status:", room.audit_ready_status)
PY
```

---

## 9. Run the API server and call new endpoints

```bash
uvicorn aeros.kernel.api.main:app --reload
```

In a separate terminal:

```bash
EVENT="event::pharma_osd_humidity_excursion_compression"

# Full assurance package (assessment + impact + reliability + evidence graph + dossier)
curl -s "http://127.0.0.1:8000/assurance/events/${EVENT}/full-package" | python3 -m json.tool | head -60

# Generate full evidence package (writes 8 files to artifacts/evidence/)
curl -s -X POST "http://127.0.0.1:8000/dossiers/events/${EVENT}/generate-package" | python3 -m json.tool

# Retrieve package manifest
curl -s "http://127.0.0.1:8000/dossiers/events/${EVENT}/manifest" | python3 -m json.tool

# APQR demo section (from cached workflow views)
curl -s "http://127.0.0.1:8000/apqr/enterprise_demo/demo-section" | python3 -m json.tool | head -40

# Generate APQR section on demand
curl -s -X POST "http://127.0.0.1:8000/apqr/enterprise_demo/generate-demo-section" | python3 -m json.tool | head -40

# Deviation draft for an event
curl -s "http://127.0.0.1:8000/workflows/deviation-drafts/${EVENT}" | python3 -m json.tool

# Enhanced deviation queue (includes due_status)
curl -s "http://127.0.0.1:8000/workflows/deviation-queue" | python3 -m json.tool

# Engineering reliability board (with actions, recurrence table, maintenance flags)
curl -s "http://127.0.0.1:8000/workflows/engineering-reliability-board" | python3 -m json.tool

# Plant head assurance (site risk score, risk tier, executive summary)
curl -s "http://127.0.0.1:8000/workflows/plant-head-assurance" | python3 -m json.tool

# Validation/audit control room (completeness table, audit-ready status)
curl -s "http://127.0.0.1:8000/workflows/validation-audit-room" | python3 -m json.tool
```

---

## 10. What is still scaffolded / planned for future productization

| Component | Local sandbox status | AWS production target |
|-----------|---------------------|----------------------|
| GMP dossier package | Writes files locally; SHA-256 integrity hashes; completeness score | S3 evidence lake; DynamoDB manifest index; KMS-signed package integrity |
| Evidence graph traversal | In-memory NetworkX; `to_neptune_like_triples()` export format | Amazon Neptune property graph; Neptune ML for anomaly clustering |
| Reliability intelligence | Rule-based recurrence + similarity; no ML | SageMaker time-series anomaly model; IoT SiteWise metric history |
| APQR section builder | Local Markdown + JSON output | APQR workflow service backed by Step Functions; human-approval via Cognito-authenticated UI |
| Connector ecosystem | Simulated BMS/MQTT/OPC-UA; file-import connector | Native connectors for Rockwell, Siemens, Honeywell, SAP PM/QM, OSI PI; Greengrass V2 edge components |
| Workflow personas | In-memory views returned by API | Cognito-authenticated persona portals; real-time event push via AppSync/WebSocket |
| 21 CFR Part 11 / GxP | Designed to support; not automatically compliant | Signed audit trails in DynamoDB; Cognito e-signature; S3 Object Lock for immutable records; customer CSV engagement required |
| Multi-tenant isolation | Single tenant/site in demo | Per-tenant VPC; per-site IoT Greengrass V2 core; separate DynamoDB tables and S3 prefixes per tenant |

---

## Learning tie-back

- **Phase 3**: Ontology, industry packs, scenario library
- **Phase 4**: Assurance engines (state-of-control, event-to-impact, evidence graph, reliability intelligence)
- **Phase 5**: Dossiers, workflows, API
- **This hardening pass**: Turned Phase 3–5 scaffolds into demonstrable product behavior — runs locally, generates inspectable files, returns rich JSON from API
- **Greengrass references**: Greengrass V2 only — see `docs/architecture/` for edge runtime design

> Areos is a system of assurance, not a system of record. Existing systems (MES, QMS, BMS, SCADA, LIMS, CMMS, ERP) monitor and store records. Areos connects signals and records to prove validated state, links plant events to product impact, generates human-approved evidence dossiers, and supports APQR/deviation workflows.
