# 00 Concept to Code Map

## Core concept map

| Concept | Meaning | AWS target | Local equivalent | Code |
|---|---|---|---|---|
| Edge gateway | OT collector / protocol bridge | AWS IoT Greengrass V2 component | Python poll loop | `ingestion/edge_gateway.py` |
| State of control | Validated condition of process/environment | Lambda / Step Functions | State-of-control engine | `assurance/state_of_control.py` |
| Evidence item | Reference to audit evidence | S3 / Neptune node | Evidence graph + dossier item | `assurance/evidence_graph.py`, `dossiers/gmp_dossier.py` |
| Control plane / API | Persona workflow views | API Gateway + app services | FastAPI app | `api/main.py` |
| Industry pack | Scenario metadata and expected evidence | Tenant/site config + policy | JSON scenario library | `artifacts/scenarios/regulated_scenario_library.json` |
