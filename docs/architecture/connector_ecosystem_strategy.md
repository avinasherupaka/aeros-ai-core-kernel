# Connector Ecosystem Strategy

Phase 6 hardens the local connector harness around a read-only-first SDK that maps to the AWS-native runtime.

## Scope

- Connector SDK with manifests, data contracts, mapping rules, validation, replay, and certification checklist support.
- Local simulated connector packs for historian, QMS/MES, and CMMS/ERP/LIMS domains.
- Validation-pack generation under `artifacts/connectors/validation/`.

## Maturity framework

- L0 manual import
- L1 scheduled export
- L2 API connector
- L3 event connector
- L4 OT protocol connector
- L5 validated connector package
- L6 certified/partner connector

## AWS-native mapping

- Local file/API simulation -> tenant-site connector component or app service.
- Read-only lineage envelope -> immutable evidence and audit trail inputs.
- Replay/backfill -> controlled reprocessing window for validation and incident investigation.

## Current local packs

- Historian targets: AVEVA PI, GE Proficy Historian, AspenTech IP.21, Ignition Historian, Canary Historian.
- QMS/MES targets: Veeva Vault QMS, Honeywell/Sparta TrackWise, MasterControl QMS, Siemens Opcenter, Körber/Werum PAS-X, Rockwell PharmaSuite, Tulip.
- CMMS/ERP/LIMS targets: SAP PM/S4, IBM Maximo, Infor EAM, LabWare, STARLIMS, Thermo SampleManager, Waters Empower, Chromeleon/OpenLab.
