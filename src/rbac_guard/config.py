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
    context_enabled: bool
    business_start_hour: int
    business_end_hour: int
    context_window_seconds: int
    new_ip_bonus: int
    after_hours_bonus: int
    rare_resource_bonus: int
    repeated_denial_bonus: int
    session_chain_bonus: int


def load_config(path: Path) -> AppConfig:
    """Load and validate detector and severity configuration."""
    with path.open("rb") as stream:
        raw = tomllib.load(stream)

    severity = raw["severity"]
    password = raw["password_guessing"]
    context = raw.get("context", {})
    failures = password["failures"]
    window_seconds = password["window_seconds"]
    medium = severity["medium"]
    high = severity["high"]
    critical = severity["critical"]
    business_start_hour = context.get("business_start_hour", 8)
    business_end_hour = context.get("business_end_hour", 18)
    context_window_seconds = context.get("window_seconds", 300)
    new_ip_bonus = context.get("new_ip_bonus", 10)
    after_hours_bonus = context.get("after_hours_bonus", 8)
    rare_resource_bonus = context.get("rare_resource_bonus", 8)
    repeated_denial_bonus = context.get("repeated_denial_bonus", 12)
    session_chain_bonus = context.get("session_chain_bonus", 15)
    if not 0 < medium < high < critical <= 100:
        raise ValueError("severity thresholds must satisfy 0 < medium < high < critical <= 100")
    if failures <= 1:
        raise ValueError("password failures must be greater than 1")
    if window_seconds <= 0:
        raise ValueError("password window_seconds must be positive")
    if not 0 <= business_start_hour < business_end_hour <= 23:
        raise ValueError("business hours must satisfy 0 <= start < end <= 23")
    if context_window_seconds <= 0:
        raise ValueError("context window_seconds must be positive")
    bonuses = (
        new_ip_bonus,
        after_hours_bonus,
        rare_resource_bonus,
        repeated_denial_bonus,
        session_chain_bonus,
    )
    if any(bonus < 0 for bonus in bonuses):
        raise ValueError("context bonuses must be non-negative")

    return AppConfig(
        password_failures=failures,
        password_window_seconds=window_seconds,
        medium=medium,
        high=high,
        critical=critical,
        context_enabled=bool(context.get("enabled", False)),
        business_start_hour=business_start_hour,
        business_end_hour=business_end_hour,
        context_window_seconds=context_window_seconds,
        new_ip_bonus=new_ip_bonus,
        after_hours_bonus=after_hours_bonus,
        rare_resource_bonus=rare_resource_bonus,
        repeated_denial_bonus=repeated_denial_bonus,
        session_chain_bonus=session_chain_bonus,
    )
