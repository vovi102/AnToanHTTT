from datetime import datetime
from pathlib import Path

from rbac_guard.config import load_config
from rbac_guard.context import BehaviorProfiler
from rbac_guard.models import Event


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
