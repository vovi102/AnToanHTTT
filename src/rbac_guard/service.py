"""Application service orchestrating one analysis run."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rbac_guard.config import load_config
from rbac_guard.models import Alert, RowError, RunMetadata
from rbac_guard.parser import parse_events
from rbac_guard.rbac import RBACRepository
from rbac_guard.reporting import write_reports
from rbac_guard.rules import (
    DetectionEngine,
    PasswordGuessingRule,
    SQLInjectionRule,
    UnauthorizedAccessRule,
)
from rbac_guard.scoring import RiskScorer


@dataclass(frozen=True)
class AnalysisResult:
    alerts: tuple[Alert, ...]
    metadata: RunMetadata
    row_errors: tuple[RowError, ...]


def analyze(
    db_path: Path,
    log_path: Path,
    config_path: Path,
    output_dir: Path,
    run_at: datetime | None = None,
) -> AnalysisResult:
    """Parse, detect, score and report a log collection."""
    config = load_config(config_path)
    parsed = parse_events(log_path)
    repository = RBACRepository(db_path)
    engine = DetectionEngine(
        (
            SQLInjectionRule(),
            PasswordGuessingRule(config.password_failures, config.password_window_seconds),
            UnauthorizedAccessRule(repository),
        )
    )
    findings = engine.detect(parsed.events)
    scorer = RiskScorer(config)
    alerts = tuple(scorer.score(finding) for finding in findings)
    metadata = RunMetadata(
        run_at=run_at or datetime.now().astimezone(),
        source_file=str(log_path),
        config_file=str(config_path),
        total_rows=len(parsed.events) + len(parsed.errors),
        valid_rows=len(parsed.events),
        invalid_rows=len(parsed.errors),
        alert_count=len(alerts),
    )
    write_reports(output_dir, alerts, metadata)
    return AnalysisResult(alerts=alerts, metadata=metadata, row_errors=parsed.errors)
