from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class ConnectorMode(str, Enum):
    READ_ONLY = "read_only"


class ConnectorManifest(BaseModel):
    connector_id: str
    connector_type: str
    version: str
    tenant_id: str
    site_id: str
    mode: ConnectorMode = ConnectorMode.READ_ONLY
    source_system: str
    enabled: bool = True
    metadata: dict = Field(default_factory=dict)


class ConnectorHealth(BaseModel):
    connector_id: str
    status: str
    last_heartbeat_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = Field(default_factory=dict)
