import re


def sanitize_segment(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    if not normalized:
        raise ValueError("UNS segment cannot be empty after sanitization")
    return normalized


def build_uns_topic(
    tenant: str,
    site: str,
    area: str,
    work_center_or_room: str,
    asset: str,
    data_domain: str,
    metric: str,
) -> str:
    segments = [
        "areos",
        tenant,
        site,
        area,
        work_center_or_room,
        asset,
        data_domain,
        metric,
    ]
    return "/".join(sanitize_segment(s) for s in segments)
