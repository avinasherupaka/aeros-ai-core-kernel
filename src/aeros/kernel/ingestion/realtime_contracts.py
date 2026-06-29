"""
Real-time ingestion contracts for Areos.

Production ingestion priority order:
  1. native events/webhooks
  2. APIs/OData/REST/SOAP
  3. OT protocols via Greengrass V2/SiteWise Edge
  4. historian streaming/query APIs
  5. enterprise event bus
  6. managed transfer/SFTP fallback
  7. manual file import — legacy onboarding/backfill ONLY

File-backed connectors are LEGACY/BACKFILL/TEST HARNESS only.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class RealtimeSourceType(str, Enum):
    WEBHOOK = 'webhook'
    API_POLLING = 'api_polling'
    EVENT_STREAM = 'event_stream'
    OPCUA = 'opcua'
    MQTT = 'mqtt'
    HISTORIAN_STREAM = 'historian_stream'
    ENTERPRISE_BUS = 'enterprise_bus'
    MANAGED_TRANSFER = 'managed_transfer'
    FILE_IMPORT_LEGACY = 'file_import_legacy'


class IngestionMode(str, Enum):
    REALTIME = 'realtime'
    NEAR_REALTIME = 'near_realtime'
    BATCH_BACKFILL = 'batch_backfill'
    MANUAL_LEGACY = 'manual_legacy'


INGESTION_PRIORITY_ORDER = [
    RealtimeSourceType.WEBHOOK,
    RealtimeSourceType.API_POLLING,
    RealtimeSourceType.OPCUA,
    RealtimeSourceType.MQTT,
    RealtimeSourceType.HISTORIAN_STREAM,
    RealtimeSourceType.ENTERPRISE_BUS,
    RealtimeSourceType.MANAGED_TRANSFER,
    RealtimeSourceType.FILE_IMPORT_LEGACY,
]


class SourceSystemEvent(BaseModel):
    event_id: str
    source_system: str
    source_type: RealtimeSourceType
    tenant_id: str
    site_id: str
    timestamp: str
    parameter: str
    value: str
    unit: str
    raw_payload: dict = Field(default_factory=dict)
    schema_version: str = '1.0'


class RealtimeIngestionEnvelope(BaseModel):
    envelope_id: str
    source_event: SourceSystemEvent
    received_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ingestion_mode: IngestionMode
    fingerprint: str = ''
    is_duplicate: bool = False


class IngestionAcknowledgement(BaseModel):
    envelope_id: str
    fingerprint: str
    is_duplicate: bool
    processor_version: str
    output_reference: str
    accepted: bool
    rejection_reason: str = ''
