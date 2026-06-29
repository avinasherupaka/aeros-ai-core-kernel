# Connector SDK

The connector SDK lives in `src/aeros/kernel/connectors/`.

## Core objects

- `ConnectorManifest`
- `ConnectorCapability`
- `ConnectorDataContract`
- `ConnectorMappingRule`
- `ConnectorHealth`
- `ConnectorRunResult`
- `ConnectorValidationResult`
- `ConnectorReplayRequest`
- `BaseConnector`
- `ConnectorRegistry`
- `ConnectorCertificationChecklist`

## Supported lifecycle methods

- `connect()`
- `health_check()`
- `discover()`
- `extract()`
- `normalize()`
- `emit()`
- `replay()` / `backfill()`
- `validate_contract()`

## Local validation flow

```python
from aeros.kernel.connectors import default_connector_registry

registry = default_connector_registry()
report = registry.validate("historian-aveva-pi")
pack = registry.generate_validation_pack("historian-aveva-pi", "artifacts/connectors/validation")
```
