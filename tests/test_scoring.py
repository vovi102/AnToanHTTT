from datetime import datetime
from pathlib import Path

import pytest

from rbac_guard.config import load_config
from rbac_guard.models import ContextFinding, Finding
from rbac_guard.scoring import RiskScorer


@pytest.fixture
def scorer() -> RiskScorer:
    return RiskScorer(load_config(Path("config/default.toml")))


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "Low"),
        (29, "Low"),
        (30, "Medium"),
        (59, "Medium"),
        (60, "High"),
        (84, "High"),
        (85, "Critical"),
        (100, "Critical"),
    ],
)
def test_severity_boundaries(scorer: RiskScorer, score: int, expected: str) -> None:
    assert scorer.severity(score) == expected


def test_score_converts_finding_to_stable_alert(scorer: RiskScorer) -> None:
    finding = Finding(
        rule_id="RBAC-UNAUTHORIZED",
        risk_type="unauthorized_access",
        event_ids=("evt-1",),
        timestamp=datetime.fromisoformat("2026-06-22T14:00:00+07:00"),
        user="teller01",
        ip="10.0.0.1",
        resource="users",
        action="delete",
        evidence="permission=users:delete",
        confidence=0.95,
        rbac_denied=True,
    )

    first = scorer.score(finding)
    second = scorer.score(finding)

    assert first == second
    assert first.risk_score == 84
    assert first.severity == "High"
    assert first.alert_id.startswith("alert-")


def test_score_context_converts_context_finding_to_alert(scorer: RiskScorer) -> None:
    finding = ContextFinding(
        signal_id="CTX-NEW-IP",
        risk_type="context_anomaly",
        event_ids=("evt-1",),
        timestamp=datetime.fromisoformat("2026-06-22T09:00:00+07:00"),
        user="teller01",
        ip="198.51.100.50",
        resource="accounts",
        action="read",
        evidence="new_ip_for_user=true",
        confidence=0.8,
        bonus=10,
    )

    alert = scorer.score_context(finding)

    assert alert.rule_id == "CTX-NEW-IP"
    assert alert.risk_type == "context_anomaly"
    assert alert.risk_score == 51
    assert alert.base_score == 25
    assert alert.context_bonus == 10
    assert alert.context_signals == ("CTX-NEW-IP",)
    assert alert.context_evidence == ("new_ip_for_user=true",)


def test_score_context_caps_score_at_100(scorer: RiskScorer) -> None:
    finding = ContextFinding(
        signal_id="CTX-CHAIN",
        risk_type="context_anomaly",
        event_ids=("evt-1",),
        timestamp=datetime.fromisoformat("2026-06-22T09:00:00+07:00"),
        user="teller01",
        ip="198.51.100.50",
        resource="accounts",
        action="read",
        evidence="chain=a->b",
        confidence=1.0,
        bonus=200,
    )

    assert scorer.score_context(finding).risk_score == 100
