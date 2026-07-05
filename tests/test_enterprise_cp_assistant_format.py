"""Tests markdown formatting and masking behavior for control-plane assistant responses."""

from __future__ import annotations

import pytest

from aeros.kernel.control_plane import ControlPlaneAssistantQuery
from aeros.kernel.control_plane.service import build_control_plane_assistant_answer
from aeros.kernel.simulation.e2e_magic_suite import run_magic_e2e_suite


@pytest.fixture(scope="module")
def evidence_root(tmp_path_factory: pytest.TempPathFactory):
    root = tmp_path_factory.mktemp("enterprise-cp-assistant")
    run_magic_e2e_suite(output_root=root, max_replay_records=2)
    return root


@pytest.fixture(scope="module")
def status_answer(evidence_root):
    return build_control_plane_assistant_answer(
        ControlPlaneAssistantQuery(question="What is the system status?", persona="qa"),
        evidence_root=evidence_root,
    )


@pytest.fixture(scope="module")
def pipeline_answer(evidence_root):
    return build_control_plane_assistant_answer(
        ControlPlaneAssistantQuery(question="Show me pipeline latency.", persona="system_admin"),
        evidence_root=evidence_root,
    )


@pytest.fixture(scope="module")
def release_answer(evidence_root):
    return build_control_plane_assistant_answer(
        ControlPlaneAssistantQuery(question="Is the batch ready for release?", persona="qa"),
        evidence_root=evidence_root,
    )


@pytest.fixture(scope="module")
def qa_answer(evidence_root):
    return build_control_plane_assistant_answer(
        ControlPlaneAssistantQuery(question="What should I do next?", persona="qa"),
        evidence_root=evidence_root,
    )


@pytest.fixture(scope="module")
def admin_answer(evidence_root):
    return build_control_plane_assistant_answer(
        ControlPlaneAssistantQuery(question="Show me pipeline latency.", persona="system_admin"),
        evidence_root=evidence_root,
    )


def test_assistant_response_is_not_raw_json(status_answer):
    assert not status_answer["response_markdown"].startswith(("{", "["))


def test_assistant_response_format_is_markdown(status_answer):
    assert status_answer["response_format"] == "markdown"


def test_assistant_response_has_no_aws_arns(status_answer):
    markdown = status_answer["response_markdown"]

    assert "arn:aws:" not in markdown
    assert "sitewise::" not in markdown

    try:
        from aeros.kernel.control_plane.models import validate_no_infra_leak
    except (ImportError, ModuleNotFoundError):
        return

    assert validate_no_infra_leak({"response_markdown": markdown}) == []


def test_assistant_response_has_no_raw_connector_ids(pipeline_answer):
    markdown = pipeline_answer["response_markdown"]

    assert "historian-ignition-live" not in markdown
    assert "qms-veeva-vault-live" not in markdown
    assert "erp-sap-s4-odata-live" not in markdown


def test_assistant_response_human_approval_flag(release_answer):
    assert release_answer["human_approval_required"] is True


def test_assistant_response_has_summary(status_answer):
    assert status_answer["summary"].strip()


def test_assistant_response_has_source_table(status_answer):
    assert "| Workflow Stage | Status | Business Summary |" in status_answer["response_markdown"]
    assert "|" in status_answer["response_markdown"]


def test_assistant_qa_persona_is_role_specific(qa_answer):
    combined = f"{qa_answer['summary']}\n{qa_answer['response_markdown']}".lower()

    assert qa_answer["persona"] == "Quality Assurance (QA)"
    assert any(token in combined for token in ("qa", "release", "approval", "audit"))


def test_assistant_admin_persona_may_see_more_detail(admin_answer):
    combined = f"{admin_answer['summary']}\n{admin_answer['response_markdown']}".lower()

    assert admin_answer["persona"] == "System Administrator"
    assert admin_answer["response_format"] == "markdown"
    assert any(token in combined for token in ("pipeline", "connector", "latency"))
