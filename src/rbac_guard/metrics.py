"""Dependency-free binary classification metrics."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from rbac_guard.parser import parse_events


@dataclass(frozen=True)
class Metrics:
    tp: int
    fp: int
    fn: int
    tn: int
    precision: float
    recall: float
    f1: float


def evaluate_labels(
    expected: set[str], predicted: set[str], universe: set[str]
) -> Metrics:
    tp = len(expected & predicted)
    fp = len(predicted - expected)
    fn = len(expected - predicted)
    tn = len(universe - expected - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return Metrics(tp, fp, fn, tn, precision, recall, f1)


RISK_TYPES = ("sql_injection", "password_guessing", "unauthorized_access")


def evaluate_artifacts(
    events_path: Path,
    alerts_path: Path,
    output_path: Path,
    manifest_path: Path | None = None,
) -> dict[str, object]:
    events = parse_events(events_path).events
    alerts = json.loads(alerts_path.read_text(encoding="utf-8"))
    universe = {event.event_id for event in events}
    by_risk_type: dict[str, dict[str, int | float]] = {}
    for risk_type in RISK_TYPES:
        expected = {
            event.event_id for event in events if event.expected_label == risk_type
        }
        predicted = {
            event_id
            for alert in alerts
            if alert["risk_type"] == risk_type
            for event_id in alert["event_ids"]
        }
        values = asdict(evaluate_labels(expected, predicted, universe))
        by_risk_type[risk_type] = {
            key: round(value, 4) if isinstance(value, float) else value
            for key, value in values.items()
        }
    macro = {
        metric: round(
            sum(float(by_risk_type[risk][metric]) for risk in RISK_TYPES) / len(RISK_TYPES),
            4,
        )
        for metric in ("precision", "recall", "f1")
    }
    result: dict[str, object] = {"by_risk_type": by_risk_type, "macro_average": macro}
    if manifest_path is not None:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        campaigns = manifest.get("campaigns", [])
        by_campaign: dict[str, dict[str, int | float]] = {}
        for risk_type in RISK_TYPES:
            expected_campaigns = {
                item["campaign_id"]
                for item in campaigns
                if item["risk_type"] == risk_type
            }
            event_to_campaign = {
                event_id: item["campaign_id"]
                for item in campaigns
                if item["risk_type"] == risk_type
                for event_id in item["event_ids"]
            }
            predicted_campaigns: set[str] = set()
            for alert in alerts:
                if alert["risk_type"] != risk_type:
                    continue
                matches = {
                    event_to_campaign[event_id]
                    for event_id in alert["event_ids"]
                    if event_id in event_to_campaign
                }
                predicted_campaigns.update(matches or {f"alert:{alert['alert_id']}"})
            campaign_universe = expected_campaigns | predicted_campaigns
            values = asdict(
                evaluate_labels(expected_campaigns, predicted_campaigns, campaign_universe)
            )
            by_campaign[risk_type] = {
                key: round(value, 4) if isinstance(value, float) else value
                for key, value in values.items()
            }
        result["by_campaign"] = by_campaign
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2), encoding="utf-8")
    temporary.replace(output_path)
    return result
