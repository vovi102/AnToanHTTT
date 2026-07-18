import json
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


def test_evaluate_artifacts_reports_campaign_level_metrics(tmp_path: Path) -> None:
    events_path = tmp_path / "events.csv"
    events_path.write_text(
        "event_id,timestamp,event_type,user,ip,resource,action,status,request,details,expected_label\n"
        "e1,2026-01-01T00:00:00+00:00,authentication,u1,ip1,session,login,failed,,x,password_guessing\n"
        "e2,2026-01-01T00:00:01+00:00,authentication,u1,ip1,session,login,failed,,x,password_guessing\n"
        "e3,2026-01-01T00:01:00+00:00,authentication,u2,ip2,session,login,success,,x,benign\n",
        encoding="utf-8",
    )
    alerts_path = tmp_path / "alerts.json"
    alerts_path.write_text(
        json.dumps(
            [
                {"alert_id": "a1", "risk_type": "password_guessing", "event_ids": ["e1", "e2"]},
                {"alert_id": "a2", "risk_type": "sql_injection", "event_ids": ["e3"]},
            ]
        ),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "campaigns": [
                    {
                        "campaign_id": "pg-1",
                        "risk_type": "password_guessing",
                        "event_ids": ["e1", "e2"],
                    },
                    {
                        "campaign_id": "sqli-missed",
                        "risk_type": "sql_injection",
                        "event_ids": ["missing-event"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = evaluate_artifacts(
        events_path, alerts_path, tmp_path / "metrics.json", manifest_path
    )

    assert result["by_campaign"]["password_guessing"]["tp"] == 1
    assert result["by_campaign"]["password_guessing"]["fn"] == 0
    assert result["by_campaign"]["sql_injection"]["tp"] == 0
    assert result["by_campaign"]["sql_injection"]["fp"] == 1
    assert result["by_campaign"]["sql_injection"]["fn"] == 1
