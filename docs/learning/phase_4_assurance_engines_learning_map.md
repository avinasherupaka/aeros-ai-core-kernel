# Phase 4 Assurance Engines Learning Map

## Goal

Learn the Phase 4 path from raw event evidence to proof-oriented assurance outputs.

## Study path

### Day 1
- Read `docs/architecture/assurance_engines.md`
- Inspect `src/aeros/kernel/assurance/canonical_event.py`

### Day 2
- Inspect `src/aeros/kernel/assurance/state_of_control.py`
- Run `pytest tests/test_state_of_control.py tests/test_state_of_control_engine.py -q`

### Day 3
- Inspect `src/aeros/kernel/assurance/event_to_impact.py`
- Run `pytest tests/test_event_to_impact_engine.py tests/test_reliability_intelligence.py -q`

### Day 4
- Inspect `src/aeros/kernel/assurance/evidence_graph.py`
- Read `docs/architecture/evidence_graph_model.md`
- Run `pytest tests/test_evidence_graph.py -q`

### Day 5
- Explain the assurance chain: utility event → area → batch/product/material → quality risk → evidence → decision.
