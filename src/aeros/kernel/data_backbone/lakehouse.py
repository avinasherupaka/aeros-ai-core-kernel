"""Embedded lakehouse backbone for the Aeros control plane.

This provides a *real*, persistent analytical store built on DuckDB with the
classic medallion architecture (bronze -> silver -> gold). It intentionally
mirrors the AWS-native contracts declared in ``lakehouse_contracts.py`` while
being runnable locally with zero external services.

Zones (DuckDB schemas):
  bronze  Raw, append-only landing of observations and events as received.
  silver  Conformed, deduplicated assurance events + state-of-control + impact.
  gold    Serving marts consumed by the control-plane API (readiness, connector
          health, dossier readiness).

The store is resolved to a writable location. In the container the ``artifacts``
mount is read-only, so we prefer ``/data/cache`` (a writable named volume).
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Optional

try:  # DuckDB is optional; the backbone degrades gracefully without it.
    import duckdb  # type: ignore

    _DUCKDB_AVAILABLE = True
except Exception:  # pragma: no cover - only when wheel missing
    duckdb = None  # type: ignore
    _DUCKDB_AVAILABLE = False


def resolve_backbone_dir() -> Path:
    """Return a writable directory for the lakehouse database file."""
    candidates: list[Path] = []
    env_dir = os.getenv("AREOS_BACKBONE_DIR")
    if env_dir:
        candidates.append(Path(env_dir))
    cache_root = os.getenv("AREOS_CACHE_ROOT", "/data/cache")
    candidates.append(Path(cache_root) / "lakehouse")
    # Local development fallback: repo artifacts dir.
    candidates.append(Path(__file__).resolve().parents[4] / "artifacts" / "lakehouse")
    candidates.append(Path(os.getcwd()) / "artifacts" / "lakehouse")

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return candidate
        except Exception:
            continue
    # Last resort: a temp dir.
    import tempfile

    fallback = Path(tempfile.gettempdir()) / "aeros_lakehouse"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


class Lakehouse:
    """DuckDB-backed medallion lakehouse."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.available = _DUCKDB_AVAILABLE
        self._lock = threading.RLock()
        self.db_path = db_path or (resolve_backbone_dir() / "aeros.duckdb")
        self._con = None
        if self.available:
            # allow multi-thread access guarded by our own lock
            self._con = duckdb.connect(str(self.db_path))
            self._init_schema()

    # -- schema ---------------------------------------------------------------
    def _init_schema(self) -> None:
        with self._lock:
            c = self._con
            for zone in ("bronze", "silver", "gold"):
                c.execute(f"CREATE SCHEMA IF NOT EXISTS {zone}")

            c.execute(
                """
                CREATE TABLE IF NOT EXISTS bronze.measurements (
                    tenant_id VARCHAR, site_id VARCHAR, area_id VARCHAR,
                    asset_id VARCHAR, metric VARCHAR, value DOUBLE, unit VARCHAR,
                    ts TIMESTAMP, source_protocol VARCHAR, scenario_id VARCHAR,
                    ingested_at TIMESTAMP DEFAULT now()
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS bronze.events (
                    event_id VARCHAR, scenario_id VARCHAR, tenant_id VARCHAR,
                    site_id VARCHAR, payload JSON, ingested_at TIMESTAMP DEFAULT now()
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS silver.assurance_events (
                    event_id VARCHAR PRIMARY KEY, scenario_id VARCHAR,
                    tenant_id VARCHAR, site_id VARCHAR, area_id VARCHAR,
                    asset_id VARCHAR, room_id VARCHAR, metric VARCHAR,
                    value DOUBLE, unit VARCHAR, severity VARCHAR, status VARCHAR,
                    batch_id VARCHAR, product_id VARCHAR, phase VARCHAR, ts TIMESTAMP
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS silver.state_of_control (
                    event_id VARCHAR PRIMARY KEY, scenario_id VARCHAR,
                    outcome VARCHAR, severity VARCHAR,
                    excursion_duration_minutes DOUBLE, alert_limit DOUBLE,
                    action_limit DOUBLE, critical_limit DOUBLE, peak_value DOUBLE,
                    confidence DOUBLE
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS silver.impact_assessments (
                    event_id VARCHAR PRIMARY KEY, scenario_id VARCHAR,
                    impacted_batch_id VARCHAR, impacted_product_id VARCHAR,
                    confidence_score DOUBLE, quality_risks JSON,
                    required_evidence JSON, missing_evidence JSON
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS gold.dossier_readiness (
                    event_id VARCHAR PRIMARY KEY, tenant_id VARCHAR, site_id VARCHAR,
                    batch_id VARCHAR, completeness_pct DOUBLE, missing_count INTEGER
                )
                """
            )

    # -- ingest ---------------------------------------------------------------
    def ingest_bundle(self, bundle: Any) -> None:
        """Persist one demo event bundle through bronze -> silver -> gold."""
        if not self.available:
            return
        event = bundle.event
        assessment = bundle.assessment
        impact = bundle.impact
        dossier = bundle.dossier

        outcome = getattr(assessment.outcome, "value", str(assessment.outcome))
        completeness = getattr(dossier, "package_completeness_score", None) or 0
        if completeness <= 1:
            completeness = round(completeness * 100)

        with self._lock:
            c = self._con
            # bronze: raw event payload landing
            c.execute("DELETE FROM bronze.events WHERE event_id = ?", [event.event_id])
            c.execute(
                "INSERT INTO bronze.events (event_id, scenario_id, tenant_id, site_id, payload) VALUES (?,?,?,?,?)",
                [event.event_id, bundle.scenario_id, event.tenant_id, event.site_id, event.model_dump_json()],
            )

            # bronze: observation landing (from state-of-control observations if present)
            observations = getattr(assessment, "observations", None) or []
            c.execute("DELETE FROM bronze.measurements WHERE scenario_id = ?", [bundle.scenario_id])
            for obs in observations:
                value = getattr(obs, "value", None)
                ts = getattr(obs, "timestamp", None)
                if value is None:
                    continue
                c.execute(
                    """INSERT INTO bronze.measurements
                    (tenant_id, site_id, area_id, asset_id, metric, value, unit, ts, source_protocol, scenario_id)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    [event.tenant_id, event.site_id, event.area_id, event.asset_id, event.metric,
                     float(value), event.unit, ts, event.source_protocol, bundle.scenario_id],
                )

            # silver: conformed event
            c.execute("DELETE FROM silver.assurance_events WHERE event_id = ?", [event.event_id])
            c.execute(
                """INSERT INTO silver.assurance_events
                (event_id, scenario_id, tenant_id, site_id, area_id, asset_id, room_id, metric,
                 value, unit, severity, status, batch_id, product_id, phase, ts)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [event.event_id, bundle.scenario_id, event.tenant_id, event.site_id, event.area_id,
                 event.asset_id, event.room_id, event.metric, event.value, event.unit, event.severity,
                 event.status, event.batch_id, event.product_id, event.phase, event.timestamp],
            )

            # silver: state of control
            c.execute("DELETE FROM silver.state_of_control WHERE event_id = ?", [event.event_id])
            c.execute(
                """INSERT INTO silver.state_of_control
                (event_id, scenario_id, outcome, severity, excursion_duration_minutes,
                 alert_limit, action_limit, critical_limit, peak_value, confidence)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                [event.event_id, bundle.scenario_id, outcome, assessment.severity,
                 getattr(assessment, "excursion_duration_minutes", None),
                 getattr(assessment, "alert_limit", None), getattr(assessment, "action_limit", None),
                 getattr(assessment, "critical_limit", None), getattr(assessment, "peak_value", None),
                 getattr(assessment, "confidence", None)],
            )

            # silver: impact assessment
            c.execute("DELETE FROM silver.impact_assessments WHERE event_id = ?", [event.event_id])
            c.execute(
                """INSERT INTO silver.impact_assessments
                (event_id, scenario_id, impacted_batch_id, impacted_product_id, confidence_score,
                 quality_risks, required_evidence, missing_evidence)
                VALUES (?,?,?,?,?,?,?,?)""",
                [event.event_id, bundle.scenario_id, impact.impacted_batch_id, impact.impacted_product_id,
                 impact.confidence_score, json.dumps(list(impact.likely_quality_risks or [])),
                 json.dumps(list(impact.required_evidence or [])), json.dumps(list(impact.missing_evidence or []))],
            )

            # gold: dossier readiness mart
            c.execute("DELETE FROM gold.dossier_readiness WHERE event_id = ?", [event.event_id])
            c.execute(
                """INSERT INTO gold.dossier_readiness
                (event_id, tenant_id, site_id, batch_id, completeness_pct, missing_count)
                VALUES (?,?,?,?,?,?)""",
                [event.event_id, event.tenant_id, event.site_id, event.batch_id,
                 float(completeness), len(impact.missing_evidence or [])],
            )

    # -- query ----------------------------------------------------------------
    def query(self, sql: str, params: Optional[list] = None) -> list[dict]:
        if not self.available:
            return []
        with self._lock:
            cur = self._con.execute(sql, params or [])
            columns = [d[0] for d in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def table_counts(self) -> dict[str, int]:
        if not self.available:
            return {}
        counts: dict[str, int] = {}
        for zone, table in [
            ("bronze", "measurements"), ("bronze", "events"),
            ("silver", "assurance_events"), ("silver", "state_of_control"),
            ("silver", "impact_assessments"), ("gold", "dossier_readiness"),
        ]:
            try:
                rows = self.query(f"SELECT count(*) AS n FROM {zone}.{table}")
                counts[f"{zone}.{table}"] = int(rows[0]["n"]) if rows else 0
            except Exception:
                counts[f"{zone}.{table}"] = 0
        return counts

    def export_parquet(self, out_dir: Optional[Path] = None) -> list[str]:
        """Export gold marts to parquet (demonstrates open-format serving)."""
        if not self.available:
            return []
        target = out_dir or (self.db_path.parent / "parquet")
        target.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        with self._lock:
            for zone, table in [("gold", "dossier_readiness"), ("silver", "assurance_events")]:
                path = target / f"{zone}_{table}.parquet"
                try:
                    self._con.execute(
                        f"COPY (SELECT * FROM {zone}.{table}) TO '{path}' (FORMAT PARQUET)"
                    )
                    written.append(str(path))
                except Exception:
                    continue
        return written
