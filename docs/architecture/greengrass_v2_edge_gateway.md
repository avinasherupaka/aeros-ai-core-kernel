# Greengrass V2 Edge Gateway

## Positioning

- Local code in this repo is a sandbox/test harness.
- Product runtime is an AWS-native tenant-site cell using **AWS IoT Greengrass V2**.
- Areos is read-only-first for OT/GxP safety and does not create a default inbound cloud-to-PLC control path.

## Greengrass V2 core device

A site edge node runs as a **Greengrass V2 core device** and hosts Areos edge components close to OPC UA servers, file drops, and local MQTT brokers. The core device is the site execution point for connector collection, local buffering, and secure publication to AWS IoT Core and SiteWise-aligned ingestion paths.

## Components and recipes

Areos edge capabilities are packaged as **Greengrass V2 components** with component recipes, versions, and deployments.

Examples in this repo:
- `edge/greengrass/components/areos.opcua-collector/recipe.yaml`
- `edge/greengrass/components/areos.mqtt-publisher/recipe.yaml`

Expected component categories:
- Read-only OPC UA collector components
- Read-only file/historian import components
- UNS normalization/publish components
- Local health/telemetry components

## Deployments

Deployments target Greengrass V2 core devices or thing groups and define:
- component versions
- configuration values
- lifecycle commands
- rollback behavior

Areos uses Greengrass V2 component/deployment language only.

## Local component lifecycle

Local sandbox equivalent:
- `src/aeros/kernel/ingestion/edge_gateway.py`
- `src/aeros/kernel/connectors/*`

Greengrass V2 lifecycle equivalent:
- `Install`
- `Run`
- local restart/retry
- deployment revision update

## Component versioning

Use semantic component versions and promote versions through enterprise CI/CD. Validation evidence should capture:
- component version
- deployment ID
- target site/tenant cell
- test evidence and rollback evidence

## Read-only OT connector components

Default Areos stance:
- collect from OPC UA, MQTT, APIs, or files in read-only mode
- preserve tenant/site/source lineage
- preserve source quality and record references
- no direct write-back to PLC/DCS/BMS by default

## SiteWise Edge / OPC UA collector relationship

Where customers use SiteWise Edge or SiteWise OPC UA collection, Areos can align with that pattern by:
- reading existing modeled signals
- preserving source-system lineage
- linking utility/process events to batches, products, risks, and evidence

Areos does not replace SiteWise; it uses SiteWise-compatible context and assurance models.

## Control-path policy

By default there is **no inbound cloud-to-PLC control path**. If a customer later approves closed-loop actions, that belongs to a separate validated design and risk review.
