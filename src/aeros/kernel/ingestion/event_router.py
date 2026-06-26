"""
Event router for Areos — analogous to AWS IoT Rules Engine.

Routes AssuranceEvents to registered handlers based on event_type.

AWS IoT Rules Engine equivalent:
  - Rules match MQTT topic patterns and SQL-like predicates.
  - Actions forward to Lambda, SQS, EventBridge, S3, etc.

Local equivalent:
  - Python RoutingRule with event_type_filter.
  - Handler is any callable that accepts an AssuranceEvent.

Usage:
    from aeros.kernel.ingestion.event_router import EventRouter, RoutingRule
    from aeros.kernel.models.canonical import EventType

    router = EventRouter()
    router.register_rule(RoutingRule(
        rule_id="log_all",
        event_type_filter="*",
        handler=lambda e: print(f"EVENT: {e.event_type} / {e.asset_id}"),
    ))
    router.register_rule(RoutingRule(
        rule_id="breach_to_evidence",
        event_type_filter=EventType.STATE_OF_CONTROL_BREACH.value,
        handler=handle_breach,
    ))
    router.route(assurance_event)
"""

from collections.abc import Callable
from dataclasses import dataclass

from aeros.kernel.models.canonical import AssuranceEvent


@dataclass
class RoutingRule:
    """
    A single routing rule.

    rule_id:            unique identifier for this rule.
    event_type_filter:  EventType value string, or "*" to match all events.
    handler:            callable that processes the matched AssuranceEvent.
    """
    rule_id: str
    event_type_filter: str
    handler: Callable[[AssuranceEvent], None]


class EventRouter:
    """
    Routes AssuranceEvents to one or more handlers.

    Analogous to AWS IoT Rules Engine rule evaluation.
    Rules are evaluated in registration order; multiple rules may match.
    """

    def __init__(self) -> None:
        self._rules: list[RoutingRule] = []

    def register_rule(self, rule: RoutingRule) -> None:
        self._rules.append(rule)

    def route(self, event: AssuranceEvent) -> None:
        """Route a single event to all matching handlers."""
        for rule in self._rules:
            if rule.event_type_filter == "*" or rule.event_type_filter == event.event_type.value:
                rule.handler(event)

    def route_many(self, events: list[AssuranceEvent]) -> None:
        """Route a list of events."""
        for event in events:
            self.route(event)

    @property
    def rule_count(self) -> int:
        return len(self._rules)

