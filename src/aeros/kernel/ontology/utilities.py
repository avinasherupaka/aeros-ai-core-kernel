from pydantic import BaseModel


class ParameterLimitBand(BaseModel):
    min_value: float | None = None
    max_value: float | None = None


class ParameterDefinition(BaseModel):
    parameter_id: str
    unit: str
    validated_range: ParameterLimitBand | None = None
    alert_limit: ParameterLimitBand | None = None
    action_limit: ParameterLimitBand | None = None
    critical_limit: ParameterLimitBand | None = None
