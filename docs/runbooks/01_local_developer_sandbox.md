# 01 Local Developer Sandbox

Use local runtime for fast iteration without AWS credentials.

## Setup (macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
docker compose up -d mosquitto
```

## Validate

```bash
pytest -q
python -m aeros.kernel.simulation.humidity_excursion | python -m json.tool | head -20
uvicorn aeros.kernel.api.main:app --reload
```

## Role of local mode

- Simulator/test harness for domain logic and connector contracts.
- Fast CI-compatible checks.
- Not the target production runtime.
