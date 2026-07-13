from pathlib import Path

from aeros.kernel.tenancy.validation import validate_tenant


def test_acme_multi_site_config_is_valid():
    problems = validate_tenant(Path(__file__).resolve().parents[1])
    assert problems == [], "tenant config problems:\n" + "\n".join(problems)
