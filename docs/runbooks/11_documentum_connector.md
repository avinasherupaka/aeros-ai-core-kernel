# OpenText Documentum connector runbook

## Scope
- Connector ID: `dms-documentum-live`
- Source system: OpenText Documentum (D2 REST)
- Mode: read-only ingestion for document evidence metadata

## Configuration
- Register endpoint in connector manifest metadata (`live_api_base_url`, `live_api_path`)
- Keep credentials in secret manager; never hard-code in repository

## Validation steps
1. Run connector discovery endpoint and verify `dms-documentum-live` is listed.
2. Run connector health endpoint and verify `live_mode_enabled=true`.
3. Pull sample records and verify normalized `record_type=dms_document`.

## Evidence mapping
- Documentum document metadata maps to ontology type `DMSDocument`.
- Use records to support audit evidence linkage in dossiers and APQR packages.
