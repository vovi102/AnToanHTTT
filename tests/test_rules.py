from datetime import datetime

import pytest

from rbac_guard.models import Event
from rbac_guard.rules import SQLInjectionRule


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
