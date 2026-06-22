"""Validated application configuration."""

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class AppConfig:
    password_failures: int
    password_window_seconds: int
    medium: int
    high: int
    critical: int


def load_config(path: Path) -> AppConfig:
    """Load and validate detector and severity configuration."""
    with path.open("rb") as stream:
        raw = tomllib.load(stream)

    severity = raw["severity"]
    password = raw["password_guessing"]
    failures = password["failures"]
    window_seconds = password["window_seconds"]
    medium = severity["medium"]
    high = severity["high"]
    critical = severity["critical"]
    if not 0 < medium < high < critical <= 100:
        raise ValueError("severity thresholds must satisfy 0 < medium < high < critical <= 100")
    if failures <= 1:
        raise ValueError("password failures must be greater than 1")
    if window_seconds <= 0:
        raise ValueError("password window_seconds must be positive")

    return AppConfig(
        password_failures=failures,
        password_window_seconds=window_seconds,
        medium=medium,
        high=high,
        critical=critical,
    )
