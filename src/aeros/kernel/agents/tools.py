from __future__ import annotations

from dataclasses import dataclass

from aeros.kernel.api.demo_data import demo_event_bundles, get_demo_event_bundle, list_demo_events, workflow_views
from aeros.kernel.connectors.registry import default_connector_registry
from aeros.kernel.dossiers.apqr import build_apqr_section


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str


class AgentToolRegistry:
    def __init__(self):
        self.connector_registry = default_connector_registry()

    def list_tools(self) -> list[dict]:
        return [
            ToolDefinition("get_event", "Get the canonical event bundle for an event id.").__dict__,
            ToolDefinition("get_state_of_control", "Get the state-of-control assessment for an event.").__dict__,
            ToolDefinition("get_impact_assessment", "Get the event-to-impact assessment.").__dict__,
            ToolDefinition("get_evidence_graph", "Get the evidence graph snapshot.").__dict__,
            ToolDefinition("get_evidence_package", "Get the current evidence package/dossier.").__dict__,
            ToolDefinition("generate_evidence_package", "Generate a fresh dossier package for an event.").__dict__,
            ToolDefinition("get_similar_events", "Get recurrence/similar-event context.").__dict__,
            ToolDefinition("get_connector_health", "Get current connector health states.").__dict__,
            ToolDefinition("get_deviation_queue", "Get QA deviation queue view.").__dict__,
            ToolDefinition("get_engineering_reliability_board", "Get engineering reliability board view.").__dict__,
            ToolDefinition("get_plant_head_assurance", "Get plant head assurance summary.").__dict__,
            ToolDefinition("get_validation_audit_room", "Get validation/audit room summary.").__dict__,
            ToolDefinition("generate_apqr_section", "Generate an APQR/PQR section for a site.").__dict__,
        ]

    def resolve_event_id(self, event_id: str | None = None, *, batch_id: str | None = None) -> str:
        if event_id:
            return event_id
        if batch_id:
            for event in list_demo_events():
                if event.get("batch_id") == batch_id:
                    return event["event_id"]
        return next(iter(demo_event_bundles().keys()))

    def get_event(self, event_id: str) -> dict:
        return get_demo_event_bundle(event_id).event.model_dump(mode="json")

    def get_state_of_control(self, event_id: str) -> dict:
        return get_demo_event_bundle(event_id).assessment.model_dump(mode="json")

    def get_impact_assessment(self, event_id: str) -> dict:
        return get_demo_event_bundle(event_id).impact.model_dump(mode="json")

    def get_evidence_graph(self, event_id: str) -> dict:
        return get_demo_event_bundle(event_id).evidence_graph.model_dump(mode="json")

    def get_evidence_package(self, event_id: str) -> dict:
        return get_demo_event_bundle(event_id).dossier.model_dump(mode="json")

    def generate_evidence_package(self, event_id: str) -> dict:
        return self.get_evidence_package(event_id)

    def get_similar_events(self, event_id: str) -> dict:
        bundle = get_demo_event_bundle(event_id)
        return bundle.reliability_insight.model_dump(mode="json")

    def get_connector_health(self) -> list[dict]:
        return self.connector_registry.health()

    def get_deviation_queue(self) -> dict:
        return workflow_views()["deviation_queue"].model_dump(mode="json")

    def get_engineering_reliability_board(self) -> dict:
        return workflow_views()["engineering_reliability_board"].model_dump(mode="json")

    def get_plant_head_assurance(self) -> dict:
        return workflow_views()["plant_head_assurance"].model_dump(mode="json")

    def get_validation_audit_room(self) -> dict:
        return workflow_views()["validation_audit_room"].model_dump(mode="json")

    def generate_apqr_section(self, site_id: str) -> dict:
        bundles = list(demo_event_bundles().values())
        return build_apqr_section(
            site_id=site_id,
            events=[bundle.event for bundle in bundles],
            impacts=[bundle.impact for bundle in bundles],
            reliability_insights=[bundle.reliability_insight for bundle in bundles],
            period="2026-H1",
        ).model_dump(mode="json")
