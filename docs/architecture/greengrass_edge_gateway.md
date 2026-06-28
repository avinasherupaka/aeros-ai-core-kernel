# Greengrass Edge Gateway (Phase 2 / Week 6)

Target pattern:
- Greengrass Core deployed at site boundary.
- Read-only OPC UA/API/file collectors.
- Local buffering and retry.
- MQTT publication to AWS IoT Core UNS topics.
- No default inbound control path to PLCs.

Component recipes in `edge/greengrass/components/*` are starter scaffolds.
