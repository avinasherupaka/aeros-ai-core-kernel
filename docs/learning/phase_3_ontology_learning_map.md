# Phase 3 Ontology Learning Map

## Goal

Learn how Areos moves from a single humidity demo to a universal regulated-operations ontology.

## Study path

### Day 1
- Read `docs/ontology/core_areos_ontology.md`
- Read `docs/architecture/regulated_industry_scope_map.md`
- Inspect `src/aeros/kernel/ontology/core.py`

### Day 2
- Inspect `src/aeros/kernel/ontology/industry_packs.py`
- Open `artifacts/scenarios/regulated_scenario_library.json`
- Run `pytest tests/test_ontology_core.py tests/test_industry_packs.py -q`

### Day 3
- Compare `build_osd_topology()` with `build_demo_ontology_context()`
- Note how local sandbox models map to tenant-site cell runtime concepts

### Day 4
- Review how batch/product/material links appear in the scenario library
- Capture gaps for the next industry pack iteration

### Day 5
- Rehearse the pitch: existing systems monitor signals; Areos connects signals to validated state, product impact, and audit evidence.
