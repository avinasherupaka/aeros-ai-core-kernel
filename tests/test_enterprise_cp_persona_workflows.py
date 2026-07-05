"""Tests persona-specific control-plane workflow views returned by the API layer."""

from __future__ import annotations

import pytest

from aeros.kernel.api.main import control_plane_persona


def _persona_text(payload: dict) -> str:
    parts = [payload.get("label", ""), payload.get("objective", "")]
    parts.extend(payload.get("highlights", []))
    parts.extend(payload.get("recommended_actions", []))
    for kpi in payload.get("kpis", []):
        parts.append(str(kpi.get("name", "")))
        parts.append(str(kpi.get("value", "")))
    return " ".join(parts).lower()


def test_qa_persona_has_release_readiness_info():
    persona = control_plane_persona("qa")
    combined = _persona_text(persona)

    assert any(token in combined for token in ("release", "approval", "audit", "compliance"))


def test_plant_ops_persona_has_operational_context():
    persona = control_plane_persona("plant_ops")
    combined = _persona_text(persona)

    assert any(token in combined for token in ("risk", "operational", "batch", "triage"))


def test_system_admin_persona_has_connector_info():
    persona = control_plane_persona("system_admin")
    combined = _persona_text(persona)

    assert any(token in combined for token in ("connector", "pipeline", "topology", "latency"))


@pytest.mark.parametrize(
    ("persona_key", "raw_label"),
    [("qa", "qa"), ("plant_ops", "plant_ops")],
)
def test_persona_labels_are_human_readable(persona_key: str, raw_label: str):
    persona = control_plane_persona(persona_key)
    label = persona["label"]

    assert label != raw_label
    assert "_" not in label
    assert any(char.isupper() for char in label)


@pytest.mark.parametrize("persona_key", ["system_admin", "qa", "plant_ops", "engineering", "leadership"])
def test_all_supported_personas_return_data(persona_key: str):
    persona = control_plane_persona(persona_key)

    assert isinstance(persona, dict)
    assert persona
