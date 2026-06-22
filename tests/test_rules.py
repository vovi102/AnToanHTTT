from datetime import datetime, timedelta

import pytest

from rbac_guard.models import Event
from rbac_guard.rules import PasswordGuessingRule, SQLInjectionRule


@pytest.fixture
def event_factory():
    def make_event(**overrides: object) -> Event:
        values: dict[str, object] = {
            "event_id": "evt-1",
            "timestamp": datetime.fromisoformat("2026-06-22T09:00:00+07:00"),
            "event_type": "access",
            "user": "teller01",
            "ip": "203.0.113.10",
            "resource": "accounts",
            "action": "read",
            "status": "denied",
            "request": "GET /accounts",
            "details": "test event",
            "expected_label": "benign",
        }
        values.update(overrides)
        return Event(**values)

    return make_event


@pytest.mark.parametrize(
    ("payload", "rule_id"),
    [
        ("' OR 1=1 --", "SQLI-TAUTOLOGY"),
        ("1 UNION SELECT password FROM users", "SQLI-UNION"),
        ("1; DROP TABLE users", "SQLI-STACKED"),
        ("admin'--", "SQLI-COMMENT"),
    ],
)
def test_sqli_rule_detects_supported_patterns(event_factory, payload: str, rule_id: str) -> None:
    findings = SQLInjectionRule().evaluate((event_factory(request=payload),))

    assert len(findings) == 1
    assert findings[0].risk_type == "sql_injection"
    assert findings[0].rule_id == rule_id
    assert payload[:20] in findings[0].evidence


def test_sqli_rule_ignores_normal_search(event_factory) -> None:
    event = event_factory(request="select account type", status="allowed")

    assert SQLInjectionRule().evaluate((event,)) == ()


def _login_events(event_factory, offsets: list[int], statuses: list[str] | None = None):
    base = datetime.fromisoformat("2026-06-22T10:00:00+07:00")
    statuses = statuses or ["failed"] * len(offsets)
    return tuple(
        event_factory(
            event_id=f"login-{index}",
            timestamp=base + timedelta(seconds=offset),
            event_type="authentication",
            user="teller01",
            ip="198.51.100.50",
            resource="session",
            action="login",
            status=status,
            request="POST /login",
        )
        for index, (offset, status) in enumerate(zip(offsets, statuses, strict=True), start=1)
    )


def test_password_rule_alerts_at_threshold_within_window(event_factory) -> None:
    events = _login_events(event_factory, [0, 20, 40, 60, 80])

    findings = PasswordGuessingRule(failures=5, window_seconds=300).evaluate(events)

    assert len(findings) == 1
    assert findings[0].risk_type == "password_guessing"
    assert findings[0].repeat_count == 5
    assert findings[0].event_ids == tuple(event.event_id for event in events)


def test_password_rule_ignores_below_threshold(event_factory) -> None:
    events = _login_events(event_factory, [0, 20, 40, 60])

    assert PasswordGuessingRule(5, 300).evaluate(events) == ()


def test_password_rule_ignores_failures_spread_beyond_window(event_factory) -> None:
    events = _login_events(event_factory, [0, 100, 200, 300, 400])

    assert PasswordGuessingRule(5, 300).evaluate(events) == ()


def test_password_rule_success_resets_failure_sequence(event_factory) -> None:
    events = _login_events(
        event_factory,
        [0, 20, 40, 60, 80, 100],
        ["failed", "failed", "success", "failed", "failed", "failed"],
    )

    assert PasswordGuessingRule(5, 300).evaluate(events) == ()


def test_password_rule_sorts_events_before_evaluation(event_factory) -> None:
    events = _login_events(event_factory, [0, 20, 40, 60, 80])
    reversed_events = tuple(reversed(events))

    assert PasswordGuessingRule(5, 300).evaluate(reversed_events) == PasswordGuessingRule(
        5, 300
    ).evaluate(events)
