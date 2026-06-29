from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from aeros.kernel.connectors.manifests import (
    ConnectorCapability,
    ConnectorCertificationChecklist,
    ConnectorHealth,
    ConnectorManifest,
    ConnectorReplayRequest,
    ConnectorRunResult,
    ConnectorValidationResult,
)


class BaseConnector(ABC):
    def __init__(self, manifest: ConnectorManifest):
        self.manifest = manifest

    def connect(self) -> dict[str, Any]:
        return {
            "connector_id": self.manifest.connector_id,
            "connected": True,
            "read_only": self.manifest.mode.value == "read_only",
            "tenant_id": self.manifest.tenant_id,
            "site_id": self.manifest.site_id,
        }

    @abstractmethod
    def health(self) -> ConnectorHealth:
        raise NotImplementedError

    @abstractmethod
    def pull(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def health_check(self) -> ConnectorHealth:
        return self.health()

    def discover(self) -> dict[str, Any]:
        return {
            "connector_id": self.manifest.connector_id,
            "source_system": self.manifest.source_system,
            "capabilities": [cap.value for cap in self.manifest.capabilities],
            "data_contracts": [contract.contract_id for contract in self.manifest.data_contracts],
        }

    def extract(self) -> list[dict[str, Any]]:
        return self.pull()

    def normalize(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized = []
        for record in records:
            if "source_lineage" in record and "record" in record:
                normalized.append(record)
            else:
                normalized.append(self.with_lineage(record))
        return normalized

    def emit(self, records: list[dict[str, Any]] | None = None) -> ConnectorRunResult:
        source_records = records if records is not None else self.extract()
        normalized_records = self.normalize(source_records)
        return ConnectorRunResult(
            connector_id=self.manifest.connector_id,
            run_type="emit",
            status="success",
            records_in=len(source_records),
            records_out=len(normalized_records),
            details={"source_system": self.manifest.source_system},
            sample_output=normalized_records[:5],
        )

    def replay(self, request: ConnectorReplayRequest) -> ConnectorRunResult:
        records = self.extract()
        filtered = self._filter_by_time_window(records, request)
        return ConnectorRunResult(
            connector_id=self.manifest.connector_id,
            run_type="replay",
            status="success",
            records_in=len(records),
            records_out=len(filtered),
            details={
                "start_time": request.start_time.isoformat() if request.start_time else None,
                "end_time": request.end_time.isoformat() if request.end_time else None,
                "window_label": request.window_label,
            },
            sample_output=self.normalize(filtered)[:5],
        )

    def backfill(self, request: ConnectorReplayRequest) -> ConnectorRunResult:
        return self.replay(request)

    def validate_contract(self) -> ConnectorValidationResult:
        errors = []
        warnings = []
        if not self.manifest.data_contracts:
            errors.append("Connector manifest must define at least one data contract.")
        if not self.manifest.mapping_rules:
            warnings.append("Connector manifest has no explicit mapping rules.")
        if ConnectorCapability.REPLAY not in self.manifest.capabilities:
            warnings.append("Replay/backfill capability not declared.")
        return ConnectorValidationResult(
            connector_id=self.manifest.connector_id,
            valid=not errors,
            errors=errors,
            warnings=warnings,
            manifest_summary={
                "connector_type": self.manifest.connector_type,
                "source_system": self.manifest.source_system,
                "maturity_level": self.manifest.maturity_level.value,
            },
            contract_ids=[contract.contract_id for contract in self.manifest.data_contracts],
        )

    def certification_checklist(self) -> ConnectorCertificationChecklist:
        checklist = [
            {"item": "Read-only mode", "status": "pass" if self.manifest.mode.value == "read_only" else "fail"},
            {"item": "Data contract defined", "status": "pass" if self.manifest.data_contracts else "fail"},
            {"item": "Mapping rules defined", "status": "pass" if self.manifest.mapping_rules else "warning"},
            {"item": "Replay path available", "status": "pass" if ConnectorCapability.REPLAY in self.manifest.capabilities else "warning"},
        ]
        validation = self.validate_contract()
        return ConnectorCertificationChecklist(
            connector_id=self.manifest.connector_id,
            maturity_level=self.manifest.maturity_level,
            checklist=checklist,
            ready_for_validation=validation.valid,
            ready_for_certification=validation.valid and self.manifest.maturity_level.value in {"L5_validated_connector_package", "L6_certified_partner_connector"},
        )

    def with_lineage(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            "tenant_id": self.manifest.tenant_id,
            "site_id": self.manifest.site_id,
            "connector_id": self.manifest.connector_id,
            "connector_type": self.manifest.connector_type,
            "source_system": self.manifest.source_system,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "source_lineage": {
                "connector_id": self.manifest.connector_id,
                "read_only": self.manifest.mode.value == "read_only",
                "tenant_id": self.manifest.tenant_id,
                "site_id": self.manifest.site_id,
            },
            "record": record,
        }

    def _filter_by_time_window(self, records: list[dict[str, Any]], request: ConnectorReplayRequest) -> list[dict[str, Any]]:
        filtered = []
        for record in records:
            timestamp = self._extract_timestamp(record)
            if request.start_time and timestamp and timestamp < request.start_time:
                continue
            if request.end_time and timestamp and timestamp > request.end_time:
                continue
            filtered.append(record)
        if request.max_records is not None:
            return filtered[: request.max_records]
        return filtered

    @staticmethod
    def _extract_timestamp(record: dict[str, Any]) -> datetime | None:
        for key in ("timestamp", "observed_at", "event_time", "completed_at", "sampled_at"):
            value = record.get(key)
            if not value:
                continue
            if isinstance(value, datetime):
                return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return None
