from rbac_guard.web import count_alerts, filter_alert_rows, filter_incident_rows


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


def test_filter_incident_rows_applies_user_severity_risk_and_signal() -> None:
    rows = [
        {
            "incident_id": "i1",
            "user": "teller01",
            "severity": "Critical",
            "risk_types": ["context_anomaly", "unauthorized_access"],
            "context_signals": ["CTX-NEW-IP"],
        },
        {
            "incident_id": "i2",
            "user": "auditor01",
            "severity": "High",
            "risk_types": ["context_anomaly"],
            "context_signals": ["CTX-AFTER-HOURS"],
        },
    ]

    assert filter_incident_rows(
        rows,
        users={"teller01"},
        risk_types={"unauthorized_access"},
        severities={"Critical"},
        context_signals={"CTX-NEW-IP"},
    ) == [rows[0]]
