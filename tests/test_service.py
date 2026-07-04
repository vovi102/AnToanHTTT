from datetime import datetime
from pathlib import Path

from rbac_guard.rbac import RBACRepository
from rbac_guard.service import analyze


def test_analyze_end_to_end(tmp_path: Path) -> None:
    db_path = tmp_path / "rbac.db"
    repository = RBACRepository(db_path)
    repository.initialize()
    repository.seed(Path("data/rbac_seed.json"))
    output_dir = tmp_path / "artifacts"

    result = analyze(
        db_path=db_path,
        log_path=Path("data/logs_demo.csv"),
        config_path=Path("config/default.toml"),
        output_dir=output_dir,
        run_at=datetime.fromisoformat("2026-06-22T15:00:00+07:00"),
    )

    assert result.metadata.valid_rows == 60
    assert result.metadata.invalid_rows == 0
    assert {alert.risk_type for alert in result.alerts} == {
        "sql_injection",
        "password_guessing",
        "unauthorized_access",
    }
    assert (output_dir / "alerts.csv").exists()
    assert (output_dir / "alerts.json").exists()
    assert (output_dir / "run_metadata.json").exists()
    assert not (output_dir / "context_findings.json").exists()
    assert not (output_dir / "incidents.json").exists()


def test_analyze_context_risk_writes_context_artifacts(tmp_path: Path) -> None:
    db_path = tmp_path / "rbac.db"
    repository = RBACRepository(db_path)
    repository.initialize()
    repository.seed(Path("data/rbac_seed.json"))
    output_dir = tmp_path / "artifacts"

    result = analyze(
        db_path=db_path,
        log_path=Path("data/logs_demo.csv"),
        config_path=Path("config/default.toml"),
        output_dir=output_dir,
        run_at=datetime.fromisoformat("2026-06-22T15:00:00+07:00"),
        context_risk=True,
    )

    assert result.context_findings
    assert result.incidents
    assert (output_dir / "context_findings.json").exists()
    assert (output_dir / "incidents.csv").exists()
    assert (output_dir / "incidents.json").exists()
