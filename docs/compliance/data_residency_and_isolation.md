# Data Residency and Isolation

- Default deployment guidance: `ap-south-1` where India residency is required.
- Tenant/site identifiers are embedded in topics, metadata, and evidence prefixes.
- Avoid cross-tenant joins in operational data paths.
- Use per-tenant keys/accounts for high-assurance enterprise deployments.
