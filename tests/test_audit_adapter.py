from pathlib import Path

from rbac_guard.audit_adapter import export_audit_events
from rbac_guard.parser import parse_events
from rbac_guard.rbac import RBACRepository
from rbac_guard.service import analyze


def test_exported_nova_audit_events_feed_detection_pipeline(tmp_path: Path) -> None:
    db_path = tmp_path / "nova.db"
    repository = RBACRepository(db_path)
    repository.initialize()
    repository.seed(Path("data/rbac_seed.json"))

    for _ in range(5):
        repository.audit("teller01", "session", "login", "failed", "Invalid password")
    repository.audit("teller01", "transactions", "approve", "denied", "RBAC denied")

    event_path = tmp_path / "nova-events.csv"
    exported = export_audit_events(db_path, event_path)
    parsed = parse_events(event_path)

    assert exported == 6
    assert not parsed.errors
    assert [event.event_type for event in parsed.events[:5]] == ["authentication"] * 5
    assert parsed.events[-1].event_type == "authorization"
    assert parsed.events[-1].status == "denied"
    assert all(event.ip == "nova-bank-local" for event in parsed.events)
    assert all(event.expected_label == "" for event in parsed.events)

    output = tmp_path / "artifacts"
    result = analyze(db_path, event_path, Path("config/default.toml"), output)
    assert {alert.risk_type for alert in result.alerts} == {
        "password_guessing",
        "unauthorized_access",
    }
