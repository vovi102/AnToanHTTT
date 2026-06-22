"""Normalize CSV and JSON security logs into domain events."""

import csv
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Mapping

from rbac_guard.models import Event, RowError


REQUIRED_FIELDS = {
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
}
EVENT_TYPES = {"authentication", "access", "authorization"}


class InputFileError(ValueError):
    """Raised when an input file cannot be treated as a log collection."""


@dataclass(frozen=True)
class ParseResult:
    events: tuple[Event, ...]
    errors: tuple[RowError, ...]


def _to_event(row: Mapping[str, Any]) -> Event:
    missing = REQUIRED_FIELDS.difference(row)
    if missing:
        raise ValueError(f"missing required fields: {', '.join(sorted(missing))}")
    try:
        timestamp = datetime.fromisoformat(str(row["timestamp"]))
    except ValueError as error:
        raise ValueError(f"invalid timestamp: {row['timestamp']}") from error
    event_type = str(row["event_type"])
    if event_type not in EVENT_TYPES:
        raise ValueError(f"invalid event_type: {event_type}")
    return Event(
        event_id=str(row["event_id"]),
        timestamp=timestamp,
        event_type=event_type,
        user=str(row["user"]) or None,
        ip=str(row["ip"]),
        resource=str(row["resource"]),
        action=str(row["action"]),
        status=str(row["status"]),
        request=str(row["request"]),
        details=str(row["details"]),
        expected_label=str(row["expected_label"]),
    )


def parse_events(path: Path) -> ParseResult:
    """Read CSV or JSON events and return their normalized representation."""
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            missing = REQUIRED_FIELDS.difference(reader.fieldnames or ())
            if missing:
                raise InputFileError(f"missing required fields: {', '.join(sorted(missing))}")
            numbered_rows = list(enumerate(reader, start=2))
    elif path.suffix.lower() == ".json":
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise InputFileError("JSON log must contain a JSON array")
        numbered_rows = list(enumerate(rows, start=1))
    else:
        raise InputFileError(f"unsupported log format: {path.suffix}")

    events: list[Event] = []
    errors: list[RowError] = []
    for row_number, row in numbered_rows:
        if not isinstance(row, Mapping):
            errors.append(RowError(row_number, "row must be an object", {"value": row}))
            continue
        try:
            events.append(_to_event(row))
        except (KeyError, TypeError, ValueError) as error:
            errors.append(RowError(row_number, str(error), row))
    return ParseResult(events=tuple(events), errors=tuple(errors))
