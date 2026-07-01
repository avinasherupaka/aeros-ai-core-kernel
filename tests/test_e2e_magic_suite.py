from aeros.kernel.simulation.e2e_magic_suite import run_magic_e2e_suite


def test_run_magic_e2e_suite_creates_evidence_and_summary(tmp_path):
    summary = run_magic_e2e_suite(output_root=tmp_path, max_replay_records=2)

    assert summary["status"] == "passed"
    assert summary["checks"]["first_ingestion_duplicate"] is False
    assert summary["checks"]["second_ingestion_duplicate"] is True
    assert summary["checks"]["state_of_control_outcome"] == "BREACH_CONFIRMED"
    assert summary["checks"]["package_completeness_score"] >= 0.7
    assert summary["checks"]["qa_agent_human_approval_required"] is True

    run_roots = [path for path in tmp_path.iterdir() if path.is_dir()]
    assert len(run_roots) == 1
    run_root = run_roots[0]
    assert summary["run_root"] == str(run_root)
    assert run_root.exists()
    assert (run_root / "summary.json").exists()
    assert (run_root / "01_preconditions" / "preconditions.json").exists()
    assert (run_root / "02_ingestion_and_connector_resolution" / "ingestion.json").exists()
    assert (run_root / "03_assurance_state_and_impact" / "assurance.json").exists()
    assert (run_root / "04_evidence_graph_and_dossier" / "dossier.json").exists()
    assert (run_root / "05_workflows_answers_and_personas" / "workflows_answers.json").exists()
