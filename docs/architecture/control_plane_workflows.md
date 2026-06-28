# Control Plane Workflows

Phase 5 adds non-UI workflow foundations for regulated operations assurance.

## Included workflow services

- Deviation workbench
- Engineering reliability board
- Plant head assurance view
- Validation/audit control room
- APQR/PQR section builder
- GMP evidence dossier generation

## API intent

The local FastAPI endpoints are a sandbox/test harness for these workflow services. In the AWS-native product runtime they map to tenant-site cell control-plane services with stronger persistence, identity, approval, and release controls.

## Human decision principle

AI assists evidence generation; humans approve quality decisions.
