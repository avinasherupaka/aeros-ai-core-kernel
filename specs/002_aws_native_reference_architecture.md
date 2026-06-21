# 002 AWS-native Reference Architecture

## Target architecture

Plant OT Layer → Greengrass-style Edge Gateway → IoT Core MQTT/UNS → SiteWise Asset Model → IoT Rules/Event routing → S3 + Graph/Provenance → Assurance Engines → Control Plane APIs → Bedrock/MCP agents.

## Local MVP mapping

| Target AWS Service | Local MVP equivalent |
|---|---|
| AWS IoT Greengrass | Local Python edge gateway |
| AWS IoT Core MQTT | Mosquitto |
| AWS IoT SiteWise | Local SiteWise-like asset model |
| AWS IoT Rules Engine | Local normalizer/router |
| Amazon S3 | Local artifact object store |
| Amazon Neptune | NetworkX graph adapter |
| Bedrock | Deferred deterministic local agents |

## Design constraints

- Read-only-first OT integration.
- Human approval for quality decisions.
- Tenant/site-aware canonical IDs and evidence paths.
- Event-driven processing and backpressure-ready design.
