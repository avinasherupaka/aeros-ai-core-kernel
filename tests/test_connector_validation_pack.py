from pathlib import Path

from aeros.kernel.connectors import default_connector_registry


def test_connector_validation_report_generation(tmp_path):
    registry = default_connector_registry()

    pack = registry.generate_validation_pack("historian-aveva-pi", tmp_path)

    root = Path(pack["root"])
    assert root.exists()
    assert (root / "manifest.json").exists()
    assert (root / "validation_report.json").exists()
    assert pack["validation"]["valid"] is True
