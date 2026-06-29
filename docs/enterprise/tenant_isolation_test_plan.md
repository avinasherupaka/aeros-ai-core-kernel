# Tenant Isolation Test Plan

- Connector manifests must declare `tenant_id` and `site_id`.
- Lineage envelopes must preserve tenant/site scoping through normalization.
- Demo API and agents must not mix records across connectors without explicit routing.
- Future AWS-native validation should test account/cell isolation, IAM boundaries, and data residency policy enforcement.
