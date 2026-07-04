from datetime import datetime
from pathlib import Path

from rbac_guard.config import load_config
from rbac_guard.context import BehaviorProfiler, build_incidents
from rbac_guard.models import Alert, Event
from rbac_guard.scoring import RiskScorer


def _event(
    event_id: str,
    timestamp: str,
    *,
    event_type: str = "access",
    user: str | None = "teller01",
    ip: str = "10.0.0.1",
    resource: str = "accounts",
    action: str = "read",
    status: str = "success",
) -> Event:
    return Event(
        event_id=event_id,
        timestamp=datetime.fromisoformat(timestamp),
        event_type=event_type,
        user=user,
        ip=ip,
        resource=resource,
        action=action,
        status=status,
        request="",
        details="",
        expected_label="benign",
    )


def _profiler() -> BehaviorProfiler:
    return BehaviorProfiler(load_config(Path("config/default.toml")))


def test_profiler_flags_new_ip_after_user_baseline_exists() -> None:
    findings = _profiler().analyze(
        (
            _event("evt-1", "2026-06-22T09:00:00+07:00", ip="10.0.0.1"),
            _event("evt-2", "2026-06-22T09:05:00+07:00", ip="198.51.100.50"),
        )
    )

    assert [(finding.signal_id, finding.event_ids) for finding in findings] == [
        ("CTX-NEW-IP", ("evt-2",))
    ]
    assert "new_ip_for_user=true" in findings[0].evidence
    assert findings[0].bonus == 10


def test_profiler_flags_new_ip_only_once_per_observed_ip() -> None:
    findings = _profiler().analyze(
        (
            _event("evt-1", "2026-06-22T09:00:00+07:00", ip="10.0.0.1"),
            _event(
                "evt-2",
                "2026-06-22T09:05:00+07:00",
                ip="198.51.100.50",
                status="failed",
            ),
            _event(
                "evt-3",
                "2026-06-22T09:06:00+07:00",
                ip="198.51.100.50",
                status="failed",
            ),
        )
    )

    assert [finding.signal_id for finding in findings] == ["CTX-NEW-IP"]


def test_profiler_flags_after_hours_activity() -> None:
    findings = _profiler().analyze(
        (_event("evt-1", "2026-06-22T22:15:00+07:00"),)
    )

    assert [finding.signal_id for finding in findings] == ["CTX-AFTER-HOURS"]
    assert "after_hours=true" in findings[0].evidence
    assert findings[0].bonus == 8


def test_profiler_flags_rare_resource_after_user_baseline_exists() -> None:
    findings = _profiler().analyze(
        (
            _event("evt-1", "2026-06-22T09:00:00+07:00", resource="accounts"),
            _event("evt-2", "2026-06-22T09:10:00+07:00", resource="audit_logs"),
        )
    )

    assert [(finding.signal_id, finding.event_ids) for finding in findings] == [
        ("CTX-RARE-RESOURCE", ("evt-2",))
    ]
    assert "rare_resource_for_user=true" in findings[0].evidence
    assert findings[0].bonus == 8


def test_profiler_flags_repeated_denials_in_window() -> None:
    findings = _profiler().analyze(
        (
            _event("evt-1", "2026-06-22T09:00:00+07:00", status="denied"),
            _event("evt-2", "2026-06-22T09:01:00+07:00", status="denied"),
            _event("evt-3", "2026-06-22T09:02:00+07:00", status="denied"),
        )
    )

    denial = [finding for finding in findings if finding.signal_id == "CTX-REPEATED-DENIAL"][0]
    assert denial.event_ids == ("evt-1", "evt-2", "evt-3")
    assert "denials_in_window=3" in denial.evidence
    assert denial.bonus == 12


def test_build_incidents_groups_related_alerts_by_user_ip_and_window() -> None:
    config = load_config(Path("config/default.toml"))
    alerts = (
        Alert(
            alert_id="alert-1",
            timestamp=datetime.fromisoformat("2026-06-22T09:00:00+07:00"),
            rule_id="CTX-NEW-IP",
            risk_type="context_anomaly",
            user="teller01",
            ip="198.51.100.50",
            resource="session",
            action="login",
            evidence="new_ip_for_user=true",
            risk_score=51,
            severity="Medium",
            event_ids=("evt-1",),
            context_signals=("CTX-NEW-IP",),
            context_evidence=("new_ip_for_user=true",),
        ),
        Alert(
            alert_id="alert-2",
            timestamp=datetime.fromisoformat("2026-06-22T09:03:00+07:00"),
            rule_id="RBAC-UNAUTHORIZED",
            risk_type="unauthorized_access",
            user="teller01",
            ip="198.51.100.50",
            resource="users",
            action="delete",
            evidence="permission=users:delete",
            risk_score=84,
            severity="High",
            event_ids=("evt-2",),
        ),
    )

    incidents = build_incidents(alerts, config.context_window_seconds, RiskScorer(config))

    assert len(incidents) == 1
    incident = incidents[0]
    assert incident.user == "teller01"
    assert incident.ip == "198.51.100.50"
    assert incident.risk_score == 99
    assert incident.severity == "Critical"
    assert incident.risk_types == ("context_anomaly", "unauthorized_access")
    assert incident.context_signals == ("CTX-NEW-IP",)
    assert incident.event_ids == ("evt-1", "evt-2")
    assert incident.alert_ids == ("alert-1", "alert-2")
    assert "teller01 from 198.51.100.50" in incident.summary
    assert "new_ip_for_user=true" in incident.evidence
