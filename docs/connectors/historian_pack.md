# Historian Connector Pack

`HistorianConnector` provides a deterministic local harness for file/API-like time-series extraction.

## Sample dataset

`artifacts/connectors/sample_data/historian/aveva_pi_samples.json`

## Normalized record shape

- `record_type=parameter_observation`
- `source_record_id`
- `tag`
- `asset_id`
- `observed_at`
- `value`
- `unit`

## Supported targets

- AVEVA PI
- GE Proficy Historian
- AspenTech IP.21
- Ignition Historian
- Canary Historian
