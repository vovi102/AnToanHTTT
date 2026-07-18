"""Run the frozen password-guessing threshold/window sensitivity grid."""

import json
from pathlib import Path
import tempfile

from rbac_guard.metrics import evaluate_artifacts
from rbac_guard.rbac import RBACRepository
from rbac_guard.service import analyze


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    base_config = (ROOT / "config" / "default.toml").read_text(encoding="utf-8")
    rows: list[dict[str, int | float]] = []
    with tempfile.TemporaryDirectory(prefix="rbac-holdout-") as directory:
        temporary = Path(directory)
        db_path = temporary / "rbac.db"
        repository = RBACRepository(db_path)
        repository.initialize()
        repository.seed(ROOT / "data" / "rbac_seed.json")
        for failures in (3, 5, 7):
            for window in (60, 300, 600):
                config_text = base_config.replace(
                    "failures = 5\nwindow_seconds = 300",
                    f"failures = {failures}\nwindow_seconds = {window}",
                )
                config_path = temporary / f"config-{failures}-{window}.toml"
                config_path.write_text(config_text, encoding="utf-8")
                output_dir = temporary / f"run-{failures}-{window}"
                analyze(
                    db_path,
                    ROOT / "data" / "logs_holdout.csv",
                    config_path,
                    output_dir,
                )
                metrics = evaluate_artifacts(
                    ROOT / "data" / "logs_holdout.csv",
                    output_dir / "alerts.json",
                    output_dir / "metrics.json",
                    ROOT / "data" / "holdout_manifest.json",
                )
                event = metrics["by_risk_type"]["password_guessing"]
                campaign = metrics["by_campaign"]["password_guessing"]
                rows.append(
                    {
                        "failures": failures,
                        "window_seconds": window,
                        "event_precision": event["precision"],
                        "event_recall": event["recall"],
                        "event_f1": event["f1"],
                        "campaign_precision": campaign["precision"],
                        "campaign_recall": campaign["recall"],
                        "campaign_f1": campaign["f1"],
                    }
                )
    destination = ROOT / "artifacts" / "holdout_sensitivity.json"
    destination.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
