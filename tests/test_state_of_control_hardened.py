from datetime import datetime, timezone, timedelta
from aeros.kernel.assurance.state_of_control import (
    ParameterLimits, ParameterObservation, LimitBand, evaluate_state_of_control
)
from aeros.kernel.models.canonical import AssessmentOutcome


def _base_kwargs():
    return dict(tenant_id="t1", site_id="s1", area_id="a1", asset_id="asset1")


def test_no_observations_returns_in_control():
    limits = [ParameterLimits(parameter="temp", unit="C", action_limit=LimitBand(max_value=25.0))]
    result = evaluate_state_of_control(observations=[], parameter_limits=limits, **_base_kwargs())
    assert result.outcome == AssessmentOutcome.IN_CONTROL
    assert result.confidence == 0.5


def test_alert_only_returns_alert_outcome():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [ParameterLimits(parameter="rh", unit="%", alert_limit=LimitBand(max_value=55.0), action_limit=LimitBand(max_value=60.0))]
    obs = [ParameterObservation(parameter="rh", value=57.0, unit="%", timestamp=base + timedelta(minutes=i)) for i in range(3)]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs())
    assert result.outcome == AssessmentOutcome.ALERT
    assert result.severity == "medium"


def test_action_breach_returns_breach_confirmed():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [ParameterLimits(parameter="rh", unit="%", action_limit=LimitBand(max_value=60.0), duration_window_minutes=1)]
    obs = [ParameterObservation(parameter="rh", value=62.0, unit="%", timestamp=base + timedelta(minutes=i)) for i in range(3)]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs())
    assert result.outcome == AssessmentOutcome.BREACH_CONFIRMED


def test_critical_breach_severity():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [ParameterLimits(parameter="temp", unit="C", action_limit=LimitBand(max_value=25.0), critical_limit=LimitBand(max_value=30.0))]
    obs = [ParameterObservation(parameter="temp", value=32.0, unit="C", timestamp=base + timedelta(minutes=i)) for i in range(2)]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs())
    assert result.severity == "critical"


def test_bad_quality_reduces_confidence():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [ParameterLimits(parameter="rh", unit="%", action_limit=LimitBand(max_value=60.0))]
    obs = [ParameterObservation(parameter="rh", value=62.0, unit="%", timestamp=base, quality="BAD")]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs())
    assert result.confidence <= 0.5


def test_uncertain_quality_reduces_confidence():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [ParameterLimits(parameter="rh", unit="%", action_limit=LimitBand(max_value=60.0))]
    obs = [ParameterObservation(parameter="rh", value=62.0, unit="%", timestamp=base, quality="UNCERTAIN")]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs())
    assert result.confidence < 0.9


def test_multi_parameter_highest_severity():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [
        ParameterLimits(parameter="rh", unit="%", alert_limit=LimitBand(max_value=55.0)),
        ParameterLimits(parameter="temp", unit="C", action_limit=LimitBand(max_value=25.0), critical_limit=LimitBand(max_value=30.0)),
    ]
    obs = [
        ParameterObservation(parameter="rh", value=57.0, unit="%", timestamp=base),
        ParameterObservation(parameter="temp", value=32.0, unit="C", timestamp=base + timedelta(minutes=1)),
    ]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs())
    assert result.severity == "critical"
    assert result.metric == "temp"


def test_confidence_breakdown_present():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    limits = [ParameterLimits(parameter="rh", unit="%", action_limit=LimitBand(max_value=60.0))]
    obs = [ParameterObservation(parameter="rh", value=62.0, unit="%", timestamp=base + timedelta(minutes=i)) for i in range(5)]
    result = evaluate_state_of_control(observations=obs, parameter_limits=limits, **_base_kwargs(), batch_id="BATCH-001", product_id="PROD-001")
    assert isinstance(result.confidence_breakdown, dict)
    assert "source_quality" in result.confidence_breakdown
    assert result.confidence_breakdown["context_present"] is True
