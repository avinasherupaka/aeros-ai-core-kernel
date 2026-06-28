"""
Utility reading and limit model.

Utility systems (HVAC/AHU, compressed air, WFI, clean steam, chilled water) are
critical to GMP manufacturing.  This model captures individual readings and the
alert/action limit configuration that governs state-of-control assessment.
"""

from pydantic import BaseModel


class UtilityLimits(BaseModel):
    metric: str
    unit: str
    alert_limit: float | None = None
    action_limit: float | None = None
    lower_alert_limit: float | None = None
    lower_action_limit: float | None = None


class UtilityReading(BaseModel):
    tenant_id: str
    site_id: str
    asset_id: str
    metric: str
    value: float
    unit: str
    timestamp: str
    quality: str = "GOOD"
    source_system: str = ""
    above_alert: bool = False
    above_action: bool = False
