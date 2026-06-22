import csv
import json
from pathlib import Path

import pytest

from rbac_guard.parser import InputFileError, parse_events


FIELDS = [
    "event_id",
    "timestamp",
    "event_type",
    "user",
    "ip",
    "resource",
    "action",
    "status",
    "request",
    "details",
    "expected_label",
]


def test_csv_and_json_normalize_to_same_events(tmp_path: Path) -> None:
    row = {
        "event_id": "evt-001",
        "timestamp": "2026-06-22T08:00:00+07:00",
        "event_type": "access",
        "user": "teller01",
        "ip": "10.0.0.1",
        "resource": "accounts",
        "action": "read",
        "status": "allowed",
        "request": "GET /accounts/123",
        "details": "normal account lookup",
        "expected_label": "benign",
    }
    csv_path = tmp_path / "events.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(row)
    json_path = tmp_path / "events.json"
    json_path.write_text(json.dumps([row]), encoding="utf-8")

    csv_result = parse_events(csv_path)
    json_result = parse_events(json_path)

    assert csv_result.events == json_result.events
    assert csv_result.errors == ()
    assert csv_result.events[0].event_id == "evt-001"


def test_parser_isolates_invalid_rows(tmp_path: Path) -> None:
    valid = {
        "event_id": "evt-ok",
        "timestamp": "2026-06-22T08:00:00+07:00",
        "event_type": "authentication",
        "user": "teller01",
        "ip": "10.0.0.1",
        "resource": "session",
        "action": "login",
        "status": "success",
        "request": "POST /login",
        "details": "valid",
        "expected_label": "benign",
    }
    invalid = dict(valid, event_id="evt-bad", timestamp="not-a-timestamp")
    path = tmp_path / "mixed.json"
    path.write_text(json.dumps([valid, invalid]), encoding="utf-8")

    result = parse_events(path)

    assert [event.event_id for event in result.events] == ["evt-ok"]
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 2
    assert "timestamp" in result.errors[0].message


@pytest.mark.parametrize("suffix", [".txt", ".xml"])
def test_parser_rejects_unsupported_formats(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f"events{suffix}"
    path.write_text("data", encoding="utf-8")

    with pytest.raises(InputFileError, match="unsupported log format"):
        parse_events(path)


def test_parser_rejects_json_object_instead_of_array(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    path.write_text(json.dumps({"event_id": "evt-1"}), encoding="utf-8")

    with pytest.raises(InputFileError, match="JSON array"):
        parse_events(path)


def test_parser_rejects_missing_csv_headers(tmp_path: Path) -> None:
    path = tmp_path / "missing.csv"
    path.write_text("event_id,timestamp\nevt-1,2026-06-22T08:00:00+07:00\n", encoding="utf-8")

    with pytest.raises(InputFileError, match="missing required fields"):
        parse_events(path)


def test_demo_dataset_has_required_scenarios() -> None:
    events = parse_events(Path("data/logs_demo.csv")).events
    counts = {
        label: sum(event.expected_label == label for event in events)
        for label in {event.expected_label for event in events}
    }

    assert len(events) >= 60
    assert counts["benign"] >= 30
    assert counts["sql_injection"] >= 10
    assert counts["password_guessing"] >= 10
    assert counts["unauthorized_access"] >= 10
    assert parse_events(Path("data/logs_demo.json")).events
