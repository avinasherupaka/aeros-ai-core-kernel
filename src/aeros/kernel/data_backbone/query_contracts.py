"""Query contracts for future incident and assurance lake queries."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class QueryStatus(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    UNDER_REVIEW = 'under_review'
    RESOLVED = 'resolved'


class IncidentQuery(BaseModel):
    tenant_id: str
    site_id: str
    time_from: str | None = None
    time_to: str | None = None
    asset_ids: list[str] = Field(default_factory=list)
    batch_ids: list[str] = Field(default_factory=list)
    product_ids: list[str] = Field(default_factory=list)
    risk_levels: list[RiskLevel] = Field(default_factory=list)
    statuses: list[QueryStatus] = Field(default_factory=list)
    limit: int = 100
    offset: int = 0


class IncidentQueryResult(BaseModel):
    query: IncidentQuery
    total_count: int
    results: list[dict] = Field(default_factory=list)
    execution_time_ms: float
    data_backbone_version: str = '1.0'
    note: str


def execute_stub_query(query: IncidentQuery) -> IncidentQueryResult:
    """Return an empty result until the governed lake query engine is implemented."""
    return IncidentQueryResult(
        query=query,
        total_count=0,
        results=[],
        execution_time_ms=0.0,
        note=(
            'The lake query engine is not yet implemented. This stub preserves the governed '
            'query/response contract for future AWS-native backbone execution.'
        ),
    )
