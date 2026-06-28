# 05 Run the API Server

The Areos Kernel API exposes the local MVP endpoints as a FastAPI REST service.

## Start the server

```bash
source .venv/bin/activate
uvicorn aeros.kernel.api.main:app --reload
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Available endpoints

### `GET /health`
Liveness check.
```bash
curl http://localhost:8000/health
# {"status":"ok","service":"aeros-kernel"}
```

### `GET /topology`
Returns the OSD plant hierarchy: site → area → room → AHU → tablet press → active batch.
```bash
curl http://localhost:8000/topology | python3 -m json.tool
```

### `GET /scenario/humidity-excursion`
Returns the raw 60-event humidity excursion dataset including topology, limits, events, and supporting records.
```bash
curl http://localhost:8000/scenario/humidity-excursion | python3 -m json.tool | head -80
```

### `GET /state-of-control/humidity-excursion`
Runs the state-of-control engine and returns:
- `StateOfControlAssessment` (outcome, excursion_duration_minutes, breach_start/end, source_lineage)
- `AssuranceEvent` list (typed events ready for event router / evidence builder)

```bash
curl http://localhost:8000/state-of-control/humidity-excursion | python3 -m json.tool
```

Expected outcome field: `"outcome": "BREACH_CONFIRMED"`  
Expected excursion: `"excursion_duration_minutes": 22.0`

---

## Swagger UI

Open http://localhost:8000/docs in a browser for interactive API documentation.

---

## Script shortcut

```bash
./scripts/run_api.sh
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Port 8000 already in use | `uvicorn ... --port 8001` |
| `ModuleNotFoundError` | Activate venv: `source .venv/bin/activate` |
| Server starts but 404 on `/state-of-control/...` | Ensure you are on the latest code with `pip install -e ".[dev]"` |
