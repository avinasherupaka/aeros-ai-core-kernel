# Evidence Graph Model

The local Phase 4 graph is an in-memory adapter that preserves the structure needed for later Neptune mapping.

## Node types

- Event
- Batch
- Product
- MaterialLot
- Room
- Equipment
- UtilitySystem
- Sensor
- SOPClause
- Deviation
- CAPA
- WorkOrder
- LabResult
- EvidenceItem
- HumanReview
- Approval
- Risk

## Edge types

- OCCURRED_IN
- ACTIVE_DURING
- IMPACTS
- EVIDENCED_BY
- REFERENCES
- SIMILAR_TO
- MAINTAINED_BY
- CONTROLLED_BY
- HAS_RISK
- REVIEWED_BY
- APPROVED_BY
- DERIVED_FROM

## Product meaning

The graph does not replace systems of record. It links source events, operational context, quality risks, evidence requirements, and human review placeholders so Areos can produce proof.
