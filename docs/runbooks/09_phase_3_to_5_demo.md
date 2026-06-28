# 09 Phase 3 to 5 Demo

This runbook uses the **local sandbox/test harness**. It does not require AWS credentials. The AWS-native product runtime remains the tenant-site cell design described in the architecture docs.

## 1. Install and run tests

```bash
cd /home/runner/work/aeros-ai-core-kernel/aeros-ai-core-kernel
python -m pip install -e '.[dev]'
pytest -q
```

## 2. List industry packs

```bash
python - <<'PY'
from aeros.kernel.ontology.industry_packs import list_industry_packs
from pprint import pprint
pprint(list_industry_packs())
PY
```

## 3. Generate a demo event catalog

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import list_demo_events
from pprint import pprint
pprint(list_demo_events())
PY
```

## 4. Evaluate state of control

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::pharma_osd_humidity_excursion_compression')
print(bundle.assessment.model_dump(mode='json'))
PY
```

## 5. Generate an impact assessment

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::pharma_osd_humidity_excursion_compression')
print(bundle.impact.model_dump(mode='json'))
PY
```

## 6. Build the evidence graph

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::api_reactor_temperature_excursion')
print(bundle.evidence_graph.model_dump(mode='json'))
PY
```

## 7. Generate a dossier

```bash
python - <<'PY'
from aeros.kernel.api.demo_data import get_demo_event_bundle
bundle = get_demo_event_bundle('event::biotech_cold_room_temperature_excursion')
print(bundle.dossier.markdown_path)
print(bundle.dossier.json_path)
PY
```

Generated artifacts land under:

```text
artifacts/evidence/{tenant_id}/{site_id}/events/{event_id}/
```

## 8. Run the API server and call endpoints

```bash
uvicorn aeros.kernel.api.main:app --reload
```

In another terminal:

```bash
curl -s http://127.0.0.1:8000/health | python3 -m json.tool
curl -s http://127.0.0.1:8000/ontology/industry-packs | python3 -m json.tool
curl -s http://127.0.0.1:8000/scenario-library | python3 -m json.tool | head -40
curl -s http://127.0.0.1:8000/assurance/demo-events | python3 -m json.tool
curl -s http://127.0.0.1:8000/assurance/events/event::pharma_osd_humidity_excursion_compression/state-of-control | python3 -m json.tool
curl -s http://127.0.0.1:8000/assurance/events/event::pharma_osd_humidity_excursion_compression/impact | python3 -m json.tool
curl -s http://127.0.0.1:8000/assurance/events/event::pharma_osd_humidity_excursion_compression/evidence-graph | python3 -m json.tool
curl -s -X POST http://127.0.0.1:8000/dossiers/events/event::pharma_osd_humidity_excursion_compression/generate | python3 -m json.tool
curl -s http://127.0.0.1:8000/workflows/deviation-queue | python3 -m json.tool
curl -s http://127.0.0.1:8000/workflows/engineering-reliability-board | python3 -m json.tool
curl -s http://127.0.0.1:8000/workflows/plant-head-assurance | python3 -m json.tool
curl -s http://127.0.0.1:8000/workflows/validation-audit-room | python3 -m json.tool
```

## 9. Learning tie-back

- Phase 3: ontology + industry packs
- Phase 4: assurance engines
- Phase 5: dossiers + workflows + API
- Greengrass V2: architecture only in this repo; local runtime remains a sandbox/test harness
