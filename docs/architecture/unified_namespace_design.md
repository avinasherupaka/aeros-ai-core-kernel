# Unified Namespace Design

Tenant-aware UNS topic pattern:

`areos/{tenant}/{site}/{area}/{work_center_or_room}/{asset}/{data_domain}/{metric}`

Guidance:
- Keep tenant and site in every topic path.
- Normalize segments to lowercase/safe tokens.
- Scope IoT policies to tenant/site prefixes.
- Preserve lineage fields in every emitted record for assurance/evidence trails.
