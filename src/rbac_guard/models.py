"""Shared immutable domain models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: datetime
    event_type: str
    user: str | None
    ip: str
    resource: str
    action: str
    status: str
    request: str
    details: str
    expected_label: str


@dataclass(frozen=True)
class RowError:
    row_number: int
    message: str
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    risk_type: str
    event_ids: tuple[str, ...]
    timestamp: datetime
    user: str | None
    ip: str
    resource: str
    action: str
    evidence: str
    confidence: float
    repeat_count: int = 1
    rbac_denied: bool = False


@dataclass(frozen=True)
class Alert:
    alert_id: str
    timestamp: datetime
    rule_id: str
    risk_type: str
    user: str | None
    ip: str
    resource: str
    action: str
    evidence: str
    risk_score: int
    severity: str
    event_ids: tuple[str, ...]
    base_score: int | None = None
    context_bonus: int = 0
    context_signals: tuple[str, ...] = ()
    context_evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextFinding:
    signal_id: str
    risk_type: str
    event_ids: tuple[str, ...]
    timestamp: datetime
    user: str | None
    ip: str
    resource: str
    action: str
    evidence: str
    confidence: float
    bonus: int


@dataclass(frozen=True)
class Incident:
    incident_id: str
    user: str | None
    ip: str
    start_time: datetime
    end_time: datetime
    severity: str
    risk_score: int
    risk_types: tuple[str, ...]
    event_ids: tuple[str, ...]
    alert_ids: tuple[str, ...]
    summary: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class RunMetadata:
    run_at: datetime
    source_file: str
    config_file: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    alert_count: int
