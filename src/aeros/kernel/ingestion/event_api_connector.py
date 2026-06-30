"""
Generic event/API connector harness for real-time ingestion.

Accepts simulated events, validates contract, computes fingerprint, checks idempotency.
This is the production-preferred connector pattern (API/event/OT protocols).

File-backed connector (FileImportConnector) is LEGACY/BACKFILL/TEST HARNESS only.
"""
from __future__ import annotations

import uuid

from aeros.kernel.algorithms.fingerprints import EventFingerprintInput, compute_event_fingerprint
from aeros.kernel.algorithms.idempotency import IdempotencyRegistry, IdempotencyStore
from aeros.kernel.ingestion.realtime_contracts import (
    IngestionAcknowledgement,
    IngestionMode,
    RealtimeIngestionEnvelope,
    SourceSystemEvent,
)

PROCESSOR_VERSION = 'event_api_connector:1.0'


class EventApiConnector:
    """
    Generic event/API connector harness.

    In production this connects to real source system APIs, webhooks, or event streams.
    In the local sandbox/test harness it accepts simulated events via ingest_event().
    """

    def __init__(
        self,
        tenant_id: str,
        site_id: str,
        *,
        idempotency_registry: IdempotencyStore | None = None,
        bronze_writer=None,
    ) -> None:
        self.tenant_id = tenant_id
        self.site_id = site_id
        self._registry = idempotency_registry or IdempotencyRegistry()
        self._bronze_writer = bronze_writer
        self._processed: list[IngestionAcknowledgement] = []

    def ingest_event(self, event: SourceSystemEvent) -> IngestionAcknowledgement:
        """Validate, fingerprint, check idempotency, and acknowledge one event."""
        fp_input = EventFingerprintInput(
            tenant_id=event.tenant_id,
            site_id=event.site_id,
            source_system=event.source_system,
            source_record_id=event.event_id,
            source_timestamp=event.timestamp,
            parameter=event.parameter,
            value=event.value,
            unit=event.unit,
            schema_version=event.schema_version,
        )
        fingerprint = compute_event_fingerprint(fp_input)

        was_duplicate, record = self._registry.check_and_record(
            fingerprint=fingerprint,
            output_reference=event.event_id,
            processor_version=PROCESSOR_VERSION,
        )

        envelope = RealtimeIngestionEnvelope(
            envelope_id=str(uuid.uuid4()),
            source_event=event,
            ingestion_mode=IngestionMode.REALTIME,
            fingerprint=fingerprint,
            is_duplicate=was_duplicate,
        )
        ack = IngestionAcknowledgement(
            envelope_id=envelope.envelope_id,
            fingerprint=fingerprint,
            is_duplicate=was_duplicate,
            processor_version=record.processor_version,
            output_reference=event.event_id,
            accepted=True,
            rejection_reason='duplicate' if was_duplicate else '',
        )
        bronze_path = ""
        if self._bronze_writer and not was_duplicate:
            bronze_path = self._bronze_writer.write_source_event(event, fingerprint)
        if bronze_path:
            ack.output_reference = bronze_path
        self._processed.append(ack)
        return ack

    def processed_count(self) -> int:
        return len(self._processed)

    def duplicate_count(self) -> int:
        return sum(1 for a in self._processed if a.is_duplicate)
