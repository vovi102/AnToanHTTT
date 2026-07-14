from rbac_guard.web import (
    count_alerts,
    filter_alert_rows,
    filter_incident_rows,
    permission_label,
    rbac_graph,
)


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


def test_rbac_graph_shows_user_role_and_permission_path() -> None:
    graph = rbac_graph(
        [
            {
                "username": "teller01",
                "status": "active",
                "role": "teller",
                "resource": "accounts",
                "action": "read",
            }
        ]
    )

    assert '"user:teller01" -> "role:teller"' in graph
    assert '"role:teller" -> "permission:accounts:read"' in graph


def test_permission_label_uses_banking_application_language() -> None:
    assert permission_label("accounts", "read") == "Xem tài khoản khách hàng"
    assert permission_label("users", "delete") == "Xóa tài khoản người dùng"
