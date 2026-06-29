"""Deterministic path helpers for bronze/silver/gold/audit storage layouts."""

from __future__ import annotations


def bronze_path(tenant_id: str, site_id: str, source_system: str, table_name: str, date_str: str) -> str:
    return f"bronze/{tenant_id}/{site_id}/{source_system}/{table_name}/date={date_str}/"


def silver_path(tenant_id: str, site_id: str, table_name: str, date_str: str) -> str:
    return f"silver/{tenant_id}/{site_id}/{table_name}/date={date_str}/"


def gold_path(tenant_id: str, site_id: str, table_name: str, date_str: str) -> str:
    return f"gold/{tenant_id}/{site_id}/{table_name}/date={date_str}/"


def audit_path(tenant_id: str, site_id: str, table_name: str, date_str: str) -> str:
    return f"audit/{tenant_id}/{site_id}/{table_name}/date={date_str}/"


def s3_key(bucket: str, path: str) -> str:
    return f"s3://{bucket}/{path}"
