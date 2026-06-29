"""
In-memory idempotency registry (test harness).
Maps to DynamoDB/Aurora in production.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class IdempotencyRecord:
    fingerprint: str
    output_reference: str
    processor_version: str
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reprocessing_count: int = 0


class IdempotencyRegistry:
    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}

    def is_duplicate(self, fingerprint: str) -> bool:
        return fingerprint in self._records

    def check_and_record(
        self, fingerprint: str, output_reference: str, processor_version: str
    ) -> tuple[bool, IdempotencyRecord]:
        """Returns (was_duplicate, record). If duplicate, increments reprocessing_count."""
        if fingerprint in self._records:
            existing = self._records[fingerprint]
            existing.reprocessing_count += 1
            return True, existing
        record = IdempotencyRecord(
            fingerprint=fingerprint,
            output_reference=output_reference,
            processor_version=processor_version,
        )
        self._records[fingerprint] = record
        return False, record

    def get_record(self, fingerprint: str) -> IdempotencyRecord | None:
        return self._records.get(fingerprint)

    def record_count(self) -> int:
        return len(self._records)
