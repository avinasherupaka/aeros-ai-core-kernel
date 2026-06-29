from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from aeros.kernel.assurance.event_to_impact import ImpactAssessment
from aeros.kernel.assurance.reliability_intelligence import ReliabilityInsight
from aeros.kernel.models.canonical import AssuranceEvent


def _safe_path_segment(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]", "_", value)


class APQRSection(BaseModel):
    site_id: str
    utility_environmental_events: list[str] = Field(default_factory=list)
    recurrence_summary: list[str] = Field(default_factory=list)
    product_batch_risk_context: list[str] = Field(default_factory=list)
    capa_deviation_placeholders: list[str] = Field(default_factory=list)
    management_review_recommendations: list[str] = Field(default_factory=list)
    product_site_scope: dict[str, Any] = Field(default_factory=dict)
    event_table: list[dict[str, Any]] = Field(default_factory=list)
    excursion_trends: list[str] = Field(default_factory=list)
    capa_effectiveness_placeholder: list[str] = Field(default_factory=list)
    risk_themes: list[str] = Field(default_factory=list)
    open_evidence_gaps: list[str] = Field(default_factory=list)
    human_review_statement: str = ""
    period: str = ""
    markdown_path: str = ""
    json_path: str = ""


def build_apqr_section(
    *,
    site_id: str,
    events: list[AssuranceEvent],
    impacts: list[ImpactAssessment],
    reliability_insights: list[ReliabilityInsight],
    period: str = "2026-H1",
    output_root: str | Path | None = None,
) -> APQRSection:
    utility_environmental_events = [
        f"{event.metric} / {event.event_type.value} / severity={event.severity or 'unknown'}"
        for event in events
    ]
    recurrence_summary = [
        f"{insight.asset_id}: {insight.classification.value} ({insight.recurrence_count} prior similar events)"
        for insight in reliability_insights
    ]
    product_batch_risk_context = [
        f"event={impact.event_id} batch={impact.impacted_batch_id or 'n/a'} product={impact.impacted_product_id or 'n/a'} risks={', '.join(impact.likely_quality_risks)}"
        for impact in impacts
    ]
    capa_deviation_placeholders = [
        f"Deviation placeholder for {impact.event_id}; CAPA to be human-approved if risk persists."
        for impact in impacts
    ]
    management_review_recommendations = [
        "Review recurrence hotspots and chronic assets with engineering reliability board.",
        "Confirm that missing evidence items are completed before APQR closure.",
        "Use Areos as proof linkage across existing systems; do not reposition it as a system of record.",
    ]

    product_site_scope = {
        "site_id": site_id,
        "products": list({impact.impacted_product_id for impact in impacts if impact.impacted_product_id}),
        "areas": list({impact.impacted_area for impact in impacts if impact.impacted_area}),
        "period": period,
    }

    event_table = []
    for event, impact in zip(events, impacts):
        event_table.append({
            "event_id": event.event_id,
            "parameter": event.metric,
            "area": impact.impacted_area,
            "product": impact.impacted_product_id,
            "batch": impact.impacted_batch_id,
            "severity": event.severity,
            "risks": impact.likely_quality_risks,
            "missing_evidence_count": len(impact.missing_evidence),
        })

    excursion_trends = [
        f"{insight.asset_id}: {insight.recurrence_count} events in lookback window ({insight.classification.value})"
        for insight in reliability_insights
    ]

    capa_effectiveness_placeholder = [
        f"CAPA for {impact.event_id}: effectiveness check pending human review."
        for impact in impacts
    ]

    risk_themes = list({risk for impact in impacts for risk in impact.likely_quality_risks})

    open_evidence_gaps = [
        f"{impact.event_id}: {item}"
        for impact in impacts
        for item in impact.missing_evidence
    ]

    human_review_statement = "All APQR/PQR entries require human review and approval before regulatory submission. AI assists drafting; humans approve quality decisions."

    markdown_path = ""
    json_path = ""
    if output_root:
        root = Path(output_root).resolve()
        apqr_dir = root / _safe_path_segment(site_id) / "apqr" / _safe_path_segment(period)
        apqr_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = str(apqr_dir / "apqr_section.md")
        json_path = str(apqr_dir / "apqr_section.json")

        markdown = f"""# APQR Section — {site_id} — {period}

## Product/Site Scope
- Site: {site_id}
- Products: {', '.join(product_site_scope['products']) or 'None'}
- Areas: {', '.join(product_site_scope['areas']) or 'None'}
- Period: {period}

## Event Table
{chr(10).join(f"- {e['event_id']}: {e['parameter']} in {e['area']} (severity: {e['severity']}, missing evidence: {e['missing_evidence_count']})" for e in event_table)}

## Excursion Trends
{chr(10).join(f"- {trend}" for trend in excursion_trends) if excursion_trends else '- None'}

## Risk Themes
{chr(10).join(f"- {risk}" for risk in risk_themes) if risk_themes else '- None'}

## Open Evidence Gaps
{chr(10).join(f"- {gap}" for gap in open_evidence_gaps) if open_evidence_gaps else '- None'}

## CAPA Effectiveness
{chr(10).join(f"- {capa}" for capa in capa_effectiveness_placeholder) if capa_effectiveness_placeholder else '- None'}

## Human Review Statement
{human_review_statement}
"""
        Path(markdown_path).write_text(markdown)
        
        section_data = {
            "site_id": site_id,
            "period": period,
            "product_site_scope": product_site_scope,
            "event_table": event_table,
            "excursion_trends": excursion_trends,
            "risk_themes": risk_themes,
            "open_evidence_gaps": open_evidence_gaps,
            "capa_effectiveness_placeholder": capa_effectiveness_placeholder,
            "human_review_statement": human_review_statement,
            "utility_environmental_events": utility_environmental_events,
            "recurrence_summary": recurrence_summary,
            "product_batch_risk_context": product_batch_risk_context,
            "capa_deviation_placeholders": capa_deviation_placeholders,
            "management_review_recommendations": management_review_recommendations,
        }
        Path(json_path).write_text(json.dumps(section_data, indent=2))

    return APQRSection(
        site_id=site_id,
        utility_environmental_events=utility_environmental_events,
        recurrence_summary=recurrence_summary,
        product_batch_risk_context=product_batch_risk_context,
        capa_deviation_placeholders=capa_deviation_placeholders,
        management_review_recommendations=management_review_recommendations,
        product_site_scope=product_site_scope,
        event_table=event_table,
        excursion_trends=excursion_trends,
        capa_effectiveness_placeholder=capa_effectiveness_placeholder,
        risk_themes=risk_themes,
        open_evidence_gaps=open_evidence_gaps,
        human_review_statement=human_review_statement,
        period=period,
        markdown_path=markdown_path,
        json_path=json_path,
    )
