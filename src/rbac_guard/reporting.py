"""Atomic CSV and JSON alert reporting."""

import csv
from dataclasses import asdict
import io
import json
from pathlib import Path
from typing import Any

from rbac_guard.models import Alert, ContextFinding, Incident, RunMetadata


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
    "base_score",
    "context_bonus",
    "context_signals",
    "context_evidence",
]

INCIDENT_FIELDS = [
    "incident_id",
    "user",
    "ip",
    "start_time",
    "end_time",
    "severity",
    "risk_score",
    "risk_types",
    "event_ids",
    "alert_ids",
    "summary",
    "evidence",
]


def _alert_record(alert: Alert) -> dict[str, Any]:
    record = asdict(alert)
    record["timestamp"] = alert.timestamp.isoformat()
    record["event_ids"] = list(alert.event_ids)
    record["context_signals"] = list(alert.context_signals)
    record["context_evidence"] = list(alert.context_evidence)
    return record


def _context_record(finding: ContextFinding) -> dict[str, Any]:
    record = asdict(finding)
    record["timestamp"] = finding.timestamp.isoformat()
    record["event_ids"] = list(finding.event_ids)
    return record


def _incident_record(incident: Incident) -> dict[str, Any]:
    record = asdict(incident)
    record["start_time"] = incident.start_time.isoformat()
    record["end_time"] = incident.end_time.isoformat()
    record["risk_types"] = list(incident.risk_types)
    record["event_ids"] = list(incident.event_ids)
    record["alert_ids"] = list(incident.alert_ids)
    record["evidence"] = list(incident.evidence)
    return record


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write_reports(
    output_dir: Path,
    alerts: tuple[Alert, ...],
    metadata: RunMetadata,
    context_findings: tuple[ContextFinding, ...] = (),
    incidents: tuple[Incident, ...] = (),
) -> None:
    """Write alerts and run metadata without exposing partial files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [_alert_record(alert) for alert in alerts]

    csv_stream = io.StringIO(newline="")
    writer = csv.DictWriter(csv_stream, fieldnames=ALERT_FIELDS)
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                **record,
                "event_ids": "|".join(record["event_ids"]),
                "context_signals": "|".join(record["context_signals"]),
                "context_evidence": "|".join(record["context_evidence"]),
            }
        )
    _atomic_write(output_dir / "alerts.csv", csv_stream.getvalue())
    _atomic_write(output_dir / "alerts.json", json.dumps(records, indent=2, ensure_ascii=False))

    metadata_record = asdict(metadata)
    metadata_record["run_at"] = metadata.run_at.isoformat()
    _atomic_write(
        output_dir / "run_metadata.json",
        json.dumps(metadata_record, indent=2, ensure_ascii=False),
    )

    if context_findings or incidents:
        context_records = [_context_record(finding) for finding in context_findings]
        incident_records = [_incident_record(incident) for incident in incidents]
        _atomic_write(
            output_dir / "context_findings.json",
            json.dumps(context_records, indent=2, ensure_ascii=False),
        )
        incident_stream = io.StringIO(newline="")
        incident_writer = csv.DictWriter(incident_stream, fieldnames=INCIDENT_FIELDS)
        incident_writer.writeheader()
        for record in incident_records:
            incident_writer.writerow(
                {
                    **record,
                    "risk_types": "|".join(record["risk_types"]),
                    "event_ids": "|".join(record["event_ids"]),
                    "alert_ids": "|".join(record["alert_ids"]),
                    "evidence": "|".join(record["evidence"]),
                }
            )
        _atomic_write(output_dir / "incidents.csv", incident_stream.getvalue())
        _atomic_write(
            output_dir / "incidents.json",
            json.dumps(incident_records, indent=2, ensure_ascii=False),
        )
