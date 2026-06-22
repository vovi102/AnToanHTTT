from pathlib import Path
import subprocess


CLI = Path(".venv/bin/rbac-guard").resolve()


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(CLI), *arguments], capture_output=True, text=True, check=False)


def test_cli_initializes_checks_and_analyzes(tmp_path: Path) -> None:
    db_path = tmp_path / "rbac.db"
    output_dir = tmp_path / "artifacts"

    initialized = _run("init-db", "--db", str(db_path), "--seed", "data/rbac_seed.json")
    checked = _run(
        "check-access",
        "--db",
        str(db_path),
        "--user",
        "teller01",
        "--resource",
        "accounts",
        "--action",
        "read",
    )
    analyzed = _run(
        "analyze",
        "--db",
        str(db_path),
        "--log",
        "data/logs_demo.csv",
        "--config",
        "config/default.toml",
        "--output",
        str(output_dir),
    )
    evaluated = _run(
        "evaluate",
        "--alerts",
        str(output_dir / "alerts.json"),
        "--events",
        "data/logs_demo.csv",
        "--output",
        str(output_dir / "metrics.json"),
    )

    assert initialized.returncode == 0
    assert checked.returncode == 0
    assert checked.stdout.strip() == "ALLOWED"
    assert analyzed.returncode == 0
    assert "60 valid events" in analyzed.stdout
    assert (output_dir / "alerts.json").exists()
    assert evaluated.returncode == 0
    assert (output_dir / "metrics.json").exists()


def test_cli_returns_code_two_without_traceback_for_bad_input(tmp_path: Path) -> None:
    result = _run(
        "analyze",
        "--db",
        str(tmp_path / "missing.db"),
        "--log",
        str(tmp_path / "missing.csv"),
        "--config",
        "config/default.toml",
        "--output",
        str(tmp_path / "out"),
    )

    assert result.returncode == 2
    assert "error:" in result.stderr.lower()
    assert "traceback" not in result.stderr.lower()
