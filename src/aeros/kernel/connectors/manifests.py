from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ConnectorMode(str, Enum):
    READ_ONLY = "read_only"


class ConnectorMaturityLevel(str, Enum):
    L0 = "L0_manual_import"
    L1 = "L1_scheduled_export"
    L2 = "L2_api_connector"
    L3 = "L3_event_connector"
    L4 = "L4_ot_protocol_connector"
    L5 = "L5_validated_connector_package"
    L6 = "L6_certified_partner_connector"


class ConnectorCapability(str, Enum):
    CONNECT = "connect"
    HEALTH_CHECK = "health_check"
    DISCOVER = "discover"
    EXTRACT = "extract"
    NORMALIZE = "normalize"
    EMIT = "emit"
    REPLAY = "replay"
    VALIDATE_CONTRACT = "validate_contract"


class ConnectorDataContract(BaseModel):
    contract_id: str
    record_type: str
    schema_version: str = "1.0.0"
    required_fields: list[str] = Field(default_factory=list)
    examples: list[dict] = Field(default_factory=list)


class ConnectorMappingRule(BaseModel):
    source_field: str
    target_field: str
    transform: str = "identity"
    required: bool = False


class ConnectorManifest(BaseModel):
    connector_id: str
    connector_type: str
    version: str
    tenant_id: str
    site_id: str
    mode: ConnectorMode = ConnectorMode.READ_ONLY
    source_system: str
    enabled: bool = True
    maturity_level: ConnectorMaturityLevel = ConnectorMaturityLevel.L1
    pack_name: str = ""
    capabilities: list[ConnectorCapability] = Field(default_factory=list)
    data_contracts: list[ConnectorDataContract] = Field(default_factory=list)
    mapping_rules: list[ConnectorMappingRule] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _default_capabilities(self) -> "ConnectorManifest":
        if not self.capabilities:
            self.capabilities = [
                ConnectorCapability.CONNECT,
                ConnectorCapability.HEALTH_CHECK,
                ConnectorCapability.EXTRACT,
                ConnectorCapability.NORMALIZE,
                ConnectorCapability.EMIT,
            ]
        return self


class ConnectorHealth(BaseModel):
    connector_id: str
    status: str
    last_heartbeat_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = Field(default_factory=dict)


class ConnectorRunResult(BaseModel):
    connector_id: str
    run_type: str
    status: str
    records_in: int = 0
    records_out: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = Field(default_factory=dict)
    sample_output: list[dict] = Field(default_factory=list)


class ConnectorValidationResult(BaseModel):
    connector_id: str
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    manifest_summary: dict = Field(default_factory=dict)
    contract_ids: list[str] = Field(default_factory=list)


class ConnectorReplayRequest(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    max_records: int | None = None
    window_label: str = ""


class ConnectorCertificationChecklist(BaseModel):
    connector_id: str
    maturity_level: ConnectorMaturityLevel
    checklist: list[dict] = Field(default_factory=list)
    ready_for_validation: bool = False
    ready_for_certification: bool = False
