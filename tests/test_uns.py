from aeros.kernel.ot.uns import build_uns_topic, sanitize_segment


def test_build_uns_topic_tenant_aware_path():
    topic = build_uns_topic(
        tenant="acme_pharma",
        site="hyd_site_01",
        area="osd_manufacturing",
        work_center_or_room="compression_room_1",
        asset="ahu_03",
        data_domain="utility",
        metric="relative_humidity",
    )
    assert topic == "areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/utility/relative_humidity"


def test_sanitize_segment_normalizes_spaces_and_symbols():
    assert sanitize_segment("Compression Room #1") == "compression_room_1"
