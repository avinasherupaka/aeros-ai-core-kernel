# Greengrass V2 Edge Gateway (Phase 2 / Week 6)

This local repository uses a sandbox/test-harness edge gateway model that maps to an **AWS IoT Greengrass V2 core device** in the product runtime.

Target pattern:
- Greengrass V2 core device deployed at the site boundary.
- Read-only OPC UA/API/file collector components.
- Local buffering, retry, and deployment-managed component lifecycle.
- MQTT publication to AWS IoT Core UNS topics.
- No default inbound cloud-to-PLC control path.

Starter Greengrass V2 component recipes live in `edge/greengrass/components/*`.

See `docs/architecture/greengrass_v2_edge_gateway.md` for the full Phase 3–5 design notes.
