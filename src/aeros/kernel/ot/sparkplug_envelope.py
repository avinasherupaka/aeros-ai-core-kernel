from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class SparkplugInspiredEnvelope(BaseModel):
    tenant_id: str
    site_id: str
    edge_node_id: str
    device_id: str
    metric: str
    value: Any
    unit: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality: str
    sequence: int
    source_protocol: str
    source_system: str
    trace_id: str
