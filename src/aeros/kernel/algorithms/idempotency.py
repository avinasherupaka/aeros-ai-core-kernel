"""
In-memory idempotency registry (test harness).
Maps to DynamoDB/Aurora in production.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass
class IdempotencyRecord:
    fingerprint: str
    output_reference: str
    processor_version: str
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reprocessing_count: int = 0


class IdempotencyStore(Protocol):
    def is_duplicate(self, fingerprint: str) -> bool: ...
    def check_and_record(self, fingerprint: str, output_reference: str, processor_version: str) -> tuple[bool, IdempotencyRecord]: ...
    def get_record(self, fingerprint: str) -> IdempotencyRecord | None: ...
    def record_count(self) -> int: ...


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


class DynamoDBIdempotencyRegistry:
    """
    Durable idempotency registry backed by DynamoDB.
    """

    def __init__(self, table_name: str, *, region_name: str = "ap-south-1", endpoint_url: str | None = None) -> None:
        try:
            import boto3  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("boto3 is required for DynamoDBIdempotencyRegistry") from exc
        self._table = boto3.resource("dynamodb", region_name=region_name, endpoint_url=endpoint_url).Table(table_name)

    @staticmethod
    def _item_key(fingerprint: str) -> dict[str, str]:
        return {"fingerprint": fingerprint}

    @staticmethod
    def _from_item(item: dict | None) -> IdempotencyRecord | None:
        if not item:
            return None
        return IdempotencyRecord(
            fingerprint=item["fingerprint"],
            output_reference=item["output_reference"],
            processor_version=item["processor_version"],
            processed_at=datetime.fromisoformat(item["processed_at"]),
            reprocessing_count=int(item.get("reprocessing_count", 0)),
        )

    def is_duplicate(self, fingerprint: str) -> bool:
        return self.get_record(fingerprint) is not None

    def check_and_record(self, fingerprint: str, output_reference: str, processor_version: str) -> tuple[bool, IdempotencyRecord]:
        existing = self.get_record(fingerprint)
        if existing:
            updated_count = existing.reprocessing_count + 1
            self._table.update_item(
                Key=self._item_key(fingerprint),
                UpdateExpression="SET reprocessing_count = :count",
                ExpressionAttributeValues={":count": updated_count},
            )
            existing.reprocessing_count = updated_count
            return True, existing

        now = datetime.now(timezone.utc)
        try:
            self._table.put_item(
                Item={
                    "fingerprint": fingerprint,
                    "output_reference": output_reference,
                    "processor_version": processor_version,
                    "processed_at": now.isoformat(),
                    "reprocessing_count": 0,
                },
                ConditionExpression="attribute_not_exists(fingerprint)",
            )
        except Exception:
            raced = self.get_record(fingerprint)
            if raced:
                raced.reprocessing_count += 1
                self._table.update_item(
                    Key=self._item_key(fingerprint),
                    UpdateExpression="SET reprocessing_count = :count",
                    ExpressionAttributeValues={":count": raced.reprocessing_count},
                )
                return True, raced
            raise
        return False, IdempotencyRecord(
            fingerprint=fingerprint,
            output_reference=output_reference,
            processor_version=processor_version,
            processed_at=now,
            reprocessing_count=0,
        )

    def get_record(self, fingerprint: str) -> IdempotencyRecord | None:
        response = self._table.get_item(Key=self._item_key(fingerprint), ConsistentRead=True)
        return self._from_item(response.get("Item"))

    def record_count(self) -> int:
        result = self._table.scan(Select="COUNT")
        return int(result.get("Count", 0))
