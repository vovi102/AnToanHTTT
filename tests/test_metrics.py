from pathlib import Path

from rbac_guard.metrics import evaluate_artifacts, evaluate_labels
from rbac_guard.rbac import RBACRepository
from rbac_guard.service import analyze


def test_evaluate_labels_builds_expected_confusion_matrix() -> None:
    metrics = evaluate_labels(
        expected={"evt-1", "evt-2"},
        predicted={"evt-1", "evt-3"},
        universe={"evt-1", "evt-2", "evt-3", "evt-4"},
    )

    assert (metrics.tp, metrics.fp, metrics.fn, metrics.tn) == (1, 1, 1, 1)
    assert metrics.precision == metrics.recall == metrics.f1 == 0.5


def test_evaluate_labels_avoids_division_by_zero() -> None:
    metrics = evaluate_labels(expected=set(), predicted=set(), universe={"evt-1"})

    assert metrics.precision == metrics.recall == metrics.f1 == 0.0
    assert metrics.tn == 1


def test_evaluate_artifacts_writes_each_risk_type(tmp_path: Path) -> None:
    db_path = tmp_path / "rbac.db"
    repository = RBACRepository(db_path)
    repository.initialize()
    repository.seed(Path("data/rbac_seed.json"))
    artifacts = tmp_path / "artifacts"
    analyze(
        db_path,
        Path("data/logs_demo.csv"),
        Path("config/default.toml"),
        artifacts,
    )
    output_path = artifacts / "metrics.json"

    result = evaluate_artifacts(
        Path("data/logs_demo.csv"), artifacts / "alerts.json", output_path
    )

    assert set(result["by_risk_type"]) == {
        "sql_injection",
        "password_guessing",
        "unauthorized_access",
    }
    assert output_path.exists()
