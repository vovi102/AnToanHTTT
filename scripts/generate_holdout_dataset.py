"""Generate the frozen synthetic hold-out set used by the technical report."""

import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "logs_holdout.csv"
MANIFEST = ROOT / "data" / "holdout_manifest.json"
FIELDS = [
    "event_id", "timestamp", "event_type", "user", "ip", "resource",
    "action", "status", "request", "details", "expected_label",
]


def main() -> None:
    base = datetime(2026, 7, 1, 1, 0, tzinfo=timezone(timedelta(hours=7)))
    rows: list[dict[str, str]] = []
    campaigns: list[dict[str, object]] = []

    def add(**values: str) -> str:
        index = len(rows) + 1
        event_id = f"holdout-{index:03d}"
        rows.append(
            {
                "event_id": event_id,
                "timestamp": (base + timedelta(seconds=index * 20)).isoformat(),
                "event_type": values.get("event_type", "access"),
                "user": values.get("user", "teller01"),
                "ip": values.get("ip", f"203.0.113.{index % 200 + 1}"),
                "resource": values.get("resource", "accounts"),
                "action": values.get("action", "read"),
                "status": values.get("status", "allowed"),
                "request": values.get("request", "GET /accounts"),
                "details": values.get("details", "frozen hold-out scenario"),
                "expected_label": values.get("expected_label", "benign"),
            }
        )
        return event_id

    allowed = [
        ("teller01", "accounts", "read"),
        ("teller01", "accounts", "update"),
        ("auditor01", "audit_logs", "read"),
        ("admin01", "users", "delete"),
    ]
    for index in range(120):
        user, resource, action = allowed[index % len(allowed)]
        add(user=user, resource=resource, action=action, request=f"GET /{resource}?page={index}")

    hard_negative_requests = [
        "GET /search?q=select account type",
        "GET /docs?q=union customer records",
        "GET /ui?q=drop-down menu",
        "GET /math?q=or 1 equals 1",
        "POST /notes text=customer said delete later",
    ]
    for index in range(40):
        add(request=hard_negative_requests[index % len(hard_negative_requests)])

    for group in range(5):
        for attempt in range(4):
            add(
                event_type="authentication",
                user=f"ordinary{group}",
                ip=f"198.51.100.{group + 10}",
                resource="session",
                action="login",
                status="failed",
                request="POST /auth/login",
                details=f"ordinary retry {attempt + 1}/4",
            )

    detectable_sqli = [
        "GET /accounts?id=' OR 1=1 --",
        "GET /search?q=1 UNION SELECT password FROM users",
        "POST /transfer note=1; DROP TABLE audit_logs",
        "GET /profile?name=admin'--",
    ]
    evasive_sqli = [
        "GET /accounts?id=1%27%20OR%201%3D1",
        "GET /search?q=UNION/**/SELECT+password+FROM+users",
    ]
    for index in range(40):
        payload = detectable_sqli[index % 4] if index < 32 else evasive_sqli[index % 2]
        event_id = add(request=payload, expected_label="sql_injection")
        campaigns.append(
            {"campaign_id": f"sqli-{index + 1:02d}", "risk_type": "sql_injection", "event_ids": [event_id]}
        )

    for campaign_index in range(8):
        event_ids = []
        for attempt in range(5):
            event_ids.append(
                add(
                    event_type="authentication",
                    user=f"target{campaign_index}",
                    ip=f"198.51.100.{campaign_index + 100}",
                    resource="session",
                    action="login",
                    status="failed",
                    request="POST /auth/login",
                    details=f"campaign attempt {attempt + 1}/5",
                    expected_label="password_guessing",
                )
            )
        campaigns.append(
            {"campaign_id": f"pg-{campaign_index + 1:02d}", "risk_type": "password_guessing", "event_ids": event_ids}
        )

    unauthorized = [
        ("teller01", "users", "delete"),
        ("auditor01", "accounts", "update"),
        ("disabled01", "accounts", "read"),
        ("teller01", "audit_logs", "read"),
    ]
    for index in range(40):
        user, resource, action = unauthorized[index % len(unauthorized)]
        event_id = add(
            user=user,
            resource=resource,
            action=action,
            status="denied",
            request=f"POST /{resource}/{action}",
            expected_label="unauthorized_access",
        )
        campaigns.append(
            {"campaign_id": f"ua-{index + 1:02d}", "risk_type": "unauthorized_access", "event_ids": [event_id]}
        )

    assert len(rows) == 300
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "dataset_id": "rbac-guard-holdout-v1",
        "generated_at": "2026-07-19",
        "rule_freeze_commit": "fced49c",
        "provenance": "Deterministic synthetic scenarios generated after freezing baseline rules; labels are not consumed by detection.",
        "strata": {
            "benign": 180,
            "sql_injection": 40,
            "password_guessing": 40,
            "unauthorized_access": 40,
        },
        "hard_negatives": 60,
        "campaigns": campaigns,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
