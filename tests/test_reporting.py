import csv
from datetime import datetime
import json
from pathlib import Path

from rbac_guard.models import Alert, ContextFinding, Incident, RunMetadata
from rbac_guard.reporting import write_reports


def _metadata(alert_count: int) -> RunMetadata:
    return RunMetadata(
        run_at=datetime.fromisoformat("2026-06-22T15:00:00+07:00"),
        source_file="data/logs_demo.csv",
        config_file="config/default.toml",
        total_rows=60,
        valid_rows=60,
        invalid_rows=0,
        alert_count=alert_count,
    )


def test_write_reports_creates_valid_empty_outputs(tmp_path: Path) -> None:
    write_reports(tmp_path, (), _metadata(0))

    with (tmp_path / "alerts.csv").open(encoding="utf-8", newline="") as stream:
        assert list(csv.DictReader(stream)) == []
    assert json.loads((tmp_path / "alerts.json").read_text(encoding="utf-8")) == []
    assert json.loads((tmp_path / "run_metadata.json").read_text(encoding="utf-8"))[
        "alert_count"
    ] == 0


def test_write_reports_keeps_csv_and_json_record_counts_equal(tmp_path: Path) -> None:
    alert = Alert(
        alert_id="alert-123",
        timestamp=datetime.fromisoformat("2026-06-22T14:00:00+07:00"),
        rule_id="RBAC-UNAUTHORIZED",
        risk_type="unauthorized_access",
        user="teller01",
        ip="10.0.0.1",
        resource="users",
        action="delete",
        evidence="permission=users:delete",
        risk_score=84,
        severity="High",
        event_ids=("evt-1",),
    )

    write_reports(tmp_path, (alert,), _metadata(1))

    with (tmp_path / "alerts.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    json_rows = json.loads((tmp_path / "alerts.json").read_text(encoding="utf-8"))
    assert len(csv_rows) == len(json_rows) == 1
    assert json_rows[0]["event_ids"] == ["evt-1"]


def test_write_reports_writes_context_and_incident_artifacts(tmp_path: Path) -> None:
    finding = ContextFinding(
        signal_id="CTX-NEW-IP",
        risk_type="context_anomaly",
        event_ids=("evt-1",),
        timestamp=datetime.fromisoformat("2026-06-22T09:00:00+07:00"),
        user="teller01",
        ip="198.51.100.50",
        resource="accounts",
        action="read",
        evidence="new_ip_for_user=true",
        confidence=0.8,
        bonus=10,
    )
    incident = Incident(
        incident_id="incident-123",
        user="teller01",
        ip="198.51.100.50",
        start_time=datetime.fromisoformat("2026-06-22T09:00:00+07:00"),
        end_time=datetime.fromisoformat("2026-06-22T09:03:00+07:00"),
        severity="Critical",
        risk_score=99,
        risk_types=("context_anomaly", "unauthorized_access"),
        event_ids=("evt-1", "evt-2"),
        alert_ids=("alert-1", "alert-2"),
        summary="teller01 from 198.51.100.50 triggered 2 alerts",
        evidence=("new_ip_for_user=true", "permission=users:delete"),
    )

    write_reports(tmp_path, (), _metadata(0), context_findings=(finding,), incidents=(incident,))

    context_rows = json.loads((tmp_path / "context_findings.json").read_text(encoding="utf-8"))
    incident_rows = json.loads((tmp_path / "incidents.json").read_text(encoding="utf-8"))
    with (tmp_path / "incidents.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))

    assert context_rows[0]["signal_id"] == "CTX-NEW-IP"
    assert incident_rows[0]["event_ids"] == ["evt-1", "evt-2"]
    assert csv_rows[0]["risk_types"] == "context_anomaly|unauthorized_access"
