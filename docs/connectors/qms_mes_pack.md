# QMS / MES Connector Pack

Phase 6 includes simulated read-only connectors for quality and manufacturing execution records.

## QMS

- Generic `QMSConnector`
- Sample file: `artifacts/connectors/sample_data/qms/veeva_deviations.json`
- Normalizes deviations/CAPA/change-control style records into `qms_quality_record`

## MES

- Generic `MESConnector`
- Sample file: `artifacts/connectors/sample_data/mes/pasx_batch_timeline.json`
- Normalizes batch/eBR timeline records into `mes_batch_timeline`
