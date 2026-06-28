# Phase 5 Control Plane Learning Map

## Goal

Learn how the local dossier/workflow services become an AWS-native control plane later.

## Study path

### Day 1
- Read `docs/architecture/control_plane_workflows.md`
- Inspect `src/aeros/kernel/dossiers/gmp_dossier.py`

### Day 2
- Inspect `src/aeros/kernel/dossiers/apqr.py`
- Run `pytest tests/test_dossier_generation.py tests/test_apqr_builder.py -q`

### Day 3
- Inspect `src/aeros/kernel/workflows/*.py`
- Run `pytest tests/test_workflow_views.py -q`

### Day 4
- Start the API server and call workflow endpoints using `docs/runbooks/09_phase_3_to_5_demo.md`

### Day 5
- Review which parts are working locally now versus what still needs enterprise persistence, identity, and approvals.
