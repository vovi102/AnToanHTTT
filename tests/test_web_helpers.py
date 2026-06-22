from rbac_guard.web import count_alerts, filter_alert_rows


ALERTS = [
    {"alert_id": "a1", "risk_type": "sql_injection", "severity": "High"},
    {"alert_id": "a2", "risk_type": "unauthorized_access", "severity": "Critical"},
    {"alert_id": "a3", "risk_type": "sql_injection", "severity": "Critical"},
]


def test_filter_alert_rows_applies_risk_and_severity() -> None:
    assert filter_alert_rows(ALERTS, {"sql_injection"}, {"Critical"}) == [ALERTS[2]]


def test_count_alerts_groups_by_requested_field() -> None:
    assert count_alerts(ALERTS, "risk_type") == {
        "sql_injection": 2,
        "unauthorized_access": 1,
    }
    assert count_alerts([], "severity") == {}
