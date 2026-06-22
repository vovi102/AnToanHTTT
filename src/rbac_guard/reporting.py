"""Atomic CSV and JSON alert reporting."""

import csv
from dataclasses import asdict
import io
import json
from pathlib import Path
from typing import Any

from rbac_guard.models import Alert, RunMetadata


ALERT_FIELDS = [
    "alert_id",
    "timestamp",
    "rule_id",
    "risk_type",
    "user",
    "ip",
    "resource",
    "action",
    "evidence",
    "risk_score",
    "severity",
    "event_ids",
]


def _alert_record(alert: Alert) -> dict[str, Any]:
    record = asdict(alert)
    record["timestamp"] = alert.timestamp.isoformat()
    record["event_ids"] = list(alert.event_ids)
    return record


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write_reports(
    output_dir: Path, alerts: tuple[Alert, ...], metadata: RunMetadata
) -> None:
    """Write alerts and run metadata without exposing partial files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [_alert_record(alert) for alert in alerts]

    csv_stream = io.StringIO(newline="")
    writer = csv.DictWriter(csv_stream, fieldnames=ALERT_FIELDS)
    writer.writeheader()
    for record in records:
        writer.writerow({**record, "event_ids": "|".join(record["event_ids"])})
    _atomic_write(output_dir / "alerts.csv", csv_stream.getvalue())
    _atomic_write(output_dir / "alerts.json", json.dumps(records, indent=2, ensure_ascii=False))

    metadata_record = asdict(metadata)
    metadata_record["run_at"] = metadata.run_at.isoformat()
    _atomic_write(
        output_dir / "run_metadata.json",
        json.dumps(metadata_record, indent=2, ensure_ascii=False),
    )
