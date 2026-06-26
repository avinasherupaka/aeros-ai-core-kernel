# 06 Test and Debug

## Running the full test suite

```bash
source .venv/bin/activate
pytest
```

Expected: all 31 tests pass in < 1 second (no network, no Docker required).

---

## Running specific test files

```bash
# Week 1: domain models
pytest tests/test_domain_models.py -v

# Week 1–2: humidity scenario
pytest tests/test_humidity_scenario.py -v

# Week 2: UNS topic builder
pytest tests/test_uns.py -v

# Week 4: local SiteWise model
pytest tests/test_local_sitewise.py -v

# Week 5: state-of-control engine + event router
pytest tests/test_state_of_control.py -v
```

---

## Running a specific test

```bash
pytest tests/test_state_of_control.py::test_excursion_duration_is_22_minutes -v
```

---

## Verifying the simulations run as modules

```bash
python -m aeros.kernel.simulation.plant_topology
python -m aeros.kernel.simulation.humidity_excursion | python3 -m json.tool | head -20
```

---

## Verifying the API responses

```bash
uvicorn aeros.kernel.api.main:app &
sleep 2

curl -s http://localhost:8000/health | python3 -m json.tool
curl -s http://localhost:8000/state-of-control/humidity-excursion | python3 -c "
import json, sys
data = json.load(sys.stdin)
a = data['assessment']
print(f'outcome: {a[\"outcome\"]}')
print(f'excursion_duration_minutes: {a[\"excursion_duration_minutes\"]}')
print(f'events: {len(data[\"assurance_events\"])}')
"
# Expected:
# outcome: BREACH_CONFIRMED
# excursion_duration_minutes: 22.0
# events: 1
```

---

## Debugging import issues

```bash
# Verify package is installed in editable mode
pip show aeros-ai-core-kernel

# Verify import works
python -c "from aeros.kernel.assurance.state_of_control import run_humidity_state_of_control; print('OK')"
python -c "from aeros.kernel.ingestion.event_router import EventRouter; print('OK')"
```

---

## Common issues

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: aeros` | Not installed or wrong venv | `pip install -e ".[dev]"` |
| `asyncua` import error | Build tools missing on Mac | `xcode-select --install` then `pip install asyncua` |
| MQTT tests hanging | Tests should NOT require MQTT; check that no test imports broker code at module level | Review test imports |
| Pydantic validation error | Model field mismatch | Check field names match the model definition |

---

## Test coverage areas (Weeks 1–5)

| Test file | Coverage |
|---|---|
| `test_domain_models.py` | ISA-95, ISA-88, Sparkplug envelope |
| `test_humidity_scenario.py` | Scenario data: 22-minute breach, supporting records |
| `test_uns.py` | UNS topic builder, segment sanitization |
| `test_local_sitewise.py` | MeasurementReading storage, humidity transform, excursion metric |
| `test_state_of_control.py` | BREACH_CONFIRMED/ALERT/IN_CONTROL outcomes, lineage, EventRouter routing |
