from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from aeros.kernel.connectors.cmms_erp_lims_pack import CMMSConnector, ERPConnector, LIMSConnector
from aeros.kernel.connectors.dms_pack import DocumentumConnector
from aeros.kernel.connectors.historian_pack import HistorianConnector
from aeros.kernel.connectors.manifests import (
    ConnectorCapability,
    ConnectorDataContract,
    ConnectorManifest,
    ConnectorMappingRule,
    ConnectorMaturityLevel,
    ConnectorReplayRequest,
)
from aeros.kernel.connectors.qms_mes_pack import MESConnector, QMSConnector
from aeros.kernel.connectors.validation import generate_connector_validation_pack


class ConnectorRegistry:
    def __init__(self):
        self._connectors: dict[str, object] = {}

    def register(self, connector) -> None:
        self._connectors[connector.manifest.connector_id] = connector

    def get(self, connector_id: str):
        return self._connectors[connector_id]

    def list_connectors(self) -> list[dict]:
        return [connector.manifest.model_dump(mode="json") for connector in self._connectors.values()]

    def discover(self) -> list[dict]:
        return [connector.discover() for connector in self._connectors.values()]

    def health(self) -> list[dict]:
        return [connector.health_check().model_dump(mode="json") for connector in self._connectors.values()]

    def validate(self, connector_id: str) -> dict:
        return self.get(connector_id).validate_contract().model_dump(mode="json")

    def replay(self, connector_id: str, request: ConnectorReplayRequest) -> dict:
        return self.get(connector_id).replay(request).model_dump(mode="json")

    def generate_validation_pack(self, connector_id: str, output_root: str | Path) -> dict:
        return generate_connector_validation_pack(self.get(connector_id), output_root)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _sample_path(*parts: str) -> str:
    return str(_repo_root() / "artifacts" / "connectors" / "sample_data" / Path(*parts))


def _base_capabilities(*extra: ConnectorCapability) -> list[ConnectorCapability]:
    return [
        ConnectorCapability.CONNECT,
        ConnectorCapability.HEALTH_CHECK,
        ConnectorCapability.DISCOVER,
        ConnectorCapability.EXTRACT,
        ConnectorCapability.NORMALIZE,
        ConnectorCapability.EMIT,
        *extra,
    ]


def _contract(contract_id: str, record_type: str, example: dict, required_fields: list[str]) -> ConnectorDataContract:
    return ConnectorDataContract(contract_id=contract_id, record_type=record_type, required_fields=required_fields, examples=[example])


def _rule(source_field: str, target_field: str, transform: str = "identity", required: bool = False) -> ConnectorMappingRule:
    return ConnectorMappingRule(source_field=source_field, target_field=target_field, transform=transform, required=required)


@lru_cache(maxsize=1)
def default_connector_registry() -> ConnectorRegistry:
    registry = ConnectorRegistry()

    registry.register(
        HistorianConnector(
            ConnectorManifest(
                connector_id="historian-aveva-pi",
                connector_type="historian",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="AVEVA PI",
                maturity_level=ConnectorMaturityLevel.L5,
                pack_name="historian",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[
                    _contract(
                        "historian_parameter_observation",
                        "parameter_observation",
                        {"tag": "AHU-01.HUMIDITY", "value": 61.4, "unit": "%RH", "observed_at": "2026-06-01T10:00:00+00:00"},
                        ["tag", "value", "unit", "observed_at"],
                    )
                ],
                mapping_rules=[
                    _rule("tag", "tag", required=True),
                    _rule("timestamp", "observed_at", required=True),
                    _rule("value", "value", required=True),
                ],
                metadata={"targets": ["AVEVA PI", "GE Proficy Historian", "AspenTech IP.21", "Ignition Historian", "Canary Historian"]},
            ),
            _sample_path("historian", "aveva_pi_samples.json"),
        )
    )
    registry.register(
        HistorianConnector(
            ConnectorManifest(
                connector_id="historian-ignition-live",
                connector_type="historian",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="Ignition Historian",
                maturity_level=ConnectorMaturityLevel.L3,
                pack_name="historian",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[
                    _contract(
                        "historian_parameter_observation",
                        "parameter_observation",
                        {"tag": "BIO-201.TEMP", "value": 36.9, "unit": "degC", "observed_at": "2026-06-01T10:00:00+00:00"},
                        ["tag", "value", "unit", "observed_at"],
                    )
                ],
                mapping_rules=[
                    _rule("tag", "tag", required=True),
                    _rule("timestamp", "observed_at", required=True),
                    _rule("value", "value", required=True),
                ],
                metadata={"targets": ["Ignition Historian"], "connectivity": "REST API"},
            ),
            _sample_path("historian", "ignition_samples.json"),
            live_api_base_url="https://ignition.example.local",
            live_api_path="/api/v1/tags/history",
        )
    )
    registry.register(
        QMSConnector(
            ConnectorManifest(
                connector_id="qms-veeva-vault",
                connector_type="qms",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="Veeva Vault QMS",
                maturity_level=ConnectorMaturityLevel.L2,
                pack_name="qms_mes",
                capabilities=_base_capabilities(ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("qms_quality_record", "qms_quality_record", {"deviation_id": "DEV-1001", "status": "open", "batch_id": "BATCH-OSD-2026-001"}, ["deviation_id", "status"])],
                mapping_rules=[_rule("deviation_id", "source_record_id", required=True), _rule("opened_at", "event_time")],
                metadata={"targets": ["Veeva Vault QMS", "Honeywell TrackWise", "MasterControl QMS"]},
            ),
            _sample_path("qms", "veeva_deviations.json"),
        )
    )
    registry.register(
        QMSConnector(
            ConnectorManifest(
                connector_id="qms-veeva-vault-live",
                connector_type="qms",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="Veeva Vault QMS",
                maturity_level=ConnectorMaturityLevel.L3,
                pack_name="qms_mes",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("qms_quality_record", "qms_quality_record", {"deviation_id": "DEV-2101", "status": "open"}, ["deviation_id", "status"])],
                mapping_rules=[_rule("deviation_id", "source_record_id", required=True), _rule("opened_at", "event_time", required=True)],
                metadata={"targets": ["Veeva Vault QMS"], "connectivity": "Vault REST API"},
            ),
            _sample_path("qms", "veeva_deviations.json"),
            live_api_base_url="https://vault.veeva.example.com",
            live_api_path="/api/v24.1/objects/deviations",
        )
    )
    registry.register(
        MESConnector(
            ConnectorManifest(
                connector_id="mes-pharmasuite",
                connector_type="mes",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="Rockwell PharmaSuite",
                maturity_level=ConnectorMaturityLevel.L2,
                pack_name="qms_mes",
                capabilities=_base_capabilities(ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("mes_batch_timeline", "mes_batch_timeline", {"batch_id": "BATCH-OSD-2026-001", "phase": "compression", "event_time": "2026-06-01T10:05:00+00:00"}, ["batch_id", "phase", "event_time"])],
                mapping_rules=[_rule("timeline_id", "source_record_id", required=True), _rule("timestamp", "event_time", required=True)],
                metadata={"targets": ["Rockwell PharmaSuite", "Siemens Opcenter", "Körber/Werum PAS-X", "Tulip"]},
            ),
            _sample_path("mes", "pharmasuite_batch_timeline.json"),
        )
    )
    registry.register(
        CMMSConnector(
            ConnectorManifest(
                connector_id="cmms-maximo",
                connector_type="cmms",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="IBM Maximo",
                maturity_level=ConnectorMaturityLevel.L2,
                pack_name="cmms_erp_lims",
                capabilities=_base_capabilities(ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("cmms_work_order", "cmms_work_order", {"work_order_id": "WO-9001", "asset_id": "AHU-01", "completed_at": "2026-05-28T10:00:00+00:00"}, ["work_order_id", "asset_id", "completed_at"])],
                mapping_rules=[_rule("work_order_id", "source_record_id", required=True), _rule("completed_at", "completed_at", required=True)],
                metadata={"targets": ["SAP PM", "IBM Maximo", "Infor EAM"]},
            ),
            _sample_path("cmms", "maximo_work_orders.json"),
        )
    )
    registry.register(
        ERPConnector(
            ConnectorManifest(
                connector_id="erp-sap-s4",
                connector_type="erp",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="SAP S/4HANA",
                maturity_level=ConnectorMaturityLevel.L2,
                pack_name="cmms_erp_lims",
                capabilities=_base_capabilities(ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("erp_batch_genealogy", "erp_batch_genealogy", {"batch_id": "BATCH-OSD-2026-001", "product_id": "TAB-500MG", "material_lot_id": "LOT-API-100"}, ["batch_id", "product_id", "material_lot_id"])],
                mapping_rules=[_rule("genealogy_id", "source_record_id", required=True), _rule("released_at", "released_at")],
                metadata={"targets": ["SAP PM", "SAP S/4HANA"]},
            ),
            _sample_path("erp", "sap_materials.json"),
        )
    )
    registry.register(
        ERPConnector(
            ConnectorManifest(
                connector_id="erp-sap-s4-odata-live",
                connector_type="erp",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="SAP S/4HANA OData",
                maturity_level=ConnectorMaturityLevel.L3,
                pack_name="cmms_erp_lims",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("erp_batch_genealogy", "erp_batch_genealogy", {"batch_id": "BATCH-OSD-2026-001", "product_id": "TAB-500MG", "material_lot_id": "LOT-API-100"}, ["batch_id", "product_id", "material_lot_id"])],
                mapping_rules=[_rule("genealogy_id", "source_record_id", required=True), _rule("released_at", "released_at")],
                metadata={"targets": ["SAP S/4HANA"], "connectivity": "OData v4"},
            ),
            _sample_path("erp", "sap_materials.json"),
            live_api_base_url="https://sap.example.local",
            live_api_path="/sap/opu/odata4/areos/genealogy",
        )
    )
    registry.register(
        CMMSConnector(
            ConnectorManifest(
                connector_id="cmms-infor-eam-live",
                connector_type="cmms",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="Infor EAM",
                maturity_level=ConnectorMaturityLevel.L3,
                pack_name="cmms_erp_lims",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("cmms_work_order", "cmms_work_order", {"work_order_id": "WO-9001", "asset_id": "BIO-201", "completed_at": "2026-05-28T10:00:00+00:00"}, ["work_order_id", "asset_id", "completed_at"])],
                mapping_rules=[_rule("work_order_id", "source_record_id", required=True), _rule("completed_at", "completed_at", required=True)],
                metadata={"targets": ["Infor EAM"], "connectivity": "REST API"},
            ),
            _sample_path("cmms", "infor_eam_work_orders.json"),
            live_api_base_url="https://infor-eam.example.local",
            live_api_path="/api/workorders",
        )
    )
    registry.register(
        LIMSConnector(
            ConnectorManifest(
                connector_id="lims-labware",
                connector_type="lims",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="LabWare LIMS",
                maturity_level=ConnectorMaturityLevel.L2,
                pack_name="cmms_erp_lims",
                capabilities=_base_capabilities(ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("lims_result", "lims_result", {"sample_id": "S-100", "parameter": "assay", "result": 99.1}, ["sample_id", "parameter", "result"])],
                mapping_rules=[_rule("result_id", "source_record_id", required=True), _rule("sampled_at", "sampled_at")],
                metadata={"targets": ["LabWare LIMS", "STARLIMS", "Thermo SampleManager", "Waters Empower", "Chromeleon/OpenLab"]},
            ),
            _sample_path("lims", "labware_results.json"),
        )
    )
    registry.register(
        LIMSConnector(
            ConnectorManifest(
                connector_id="lims-labware-live",
                connector_type="lims",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="LabWare LIMS",
                maturity_level=ConnectorMaturityLevel.L3,
                pack_name="cmms_erp_lims",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("lims_result", "lims_result", {"sample_id": "S-100", "parameter": "bioburden", "result": 0.0}, ["sample_id", "parameter", "result"])],
                mapping_rules=[_rule("result_id", "source_record_id", required=True), _rule("sampled_at", "sampled_at")],
                metadata={"targets": ["LabWare LIMS"], "connectivity": "REST API"},
            ),
            _sample_path("lims", "labware_results.json"),
            live_api_base_url="https://labware.example.local",
            live_api_path="/api/results",
        )
    )
    registry.register(
        DocumentumConnector(
            ConnectorManifest(
                connector_id="dms-documentum-live",
                connector_type="dms",
                version="0.1.0",
                tenant_id="acme",
                site_id="hyd-01",
                source_system="OpenText Documentum",
                maturity_level=ConnectorMaturityLevel.L3,
                pack_name="dms",
                capabilities=_base_capabilities(ConnectorCapability.REPLAY, ConnectorCapability.VALIDATE_CONTRACT),
                data_contracts=[_contract("dms_document", "dms_document", {"document_id": "DOC-1001", "title": "SOP-001"}, ["document_id", "title"])],
                mapping_rules=[_rule("document_id", "source_record_id", required=True), _rule("effective_at", "effective_at")],
                metadata={"targets": ["OpenText Documentum"], "connectivity": "D2 REST"},
            ),
            _sample_path("dms", "documentum_documents.json"),
            live_api_base_url="https://documentum.example.local",
            live_api_path="/d2/api/documents",
        )
    )
    return registry
