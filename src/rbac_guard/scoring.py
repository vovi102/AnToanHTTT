"""Deterministic risk scoring and severity mapping."""

import hashlib

from rbac_guard.config import AppConfig
from rbac_guard.models import Alert, ContextFinding, Finding


BASE_SCORES = {
    "sql_injection": 45,
    "password_guessing": 40,
    "unauthorized_access": 50,
    "context_anomaly": 25,
}


class RiskScorer:
    def __init__(self, config: AppConfig):
        self.config = config

    def severity(self, score: int) -> str:
        if score >= self.config.critical:
            return "Critical"
        if score >= self.config.high:
            return "High"
        if score >= self.config.medium:
            return "Medium"
        return "Low"

    def score(self, finding: Finding) -> Alert:
        base = BASE_SCORES[finding.risk_type]
        confidence_points = round(20 * finding.confidence)
        repeat_points = min(15, max(0, finding.repeat_count - 1) * 3)
        rbac_points = 15 if finding.rbac_denied else 0
        risk_score = min(100, max(0, base + confidence_points + repeat_points + rbac_points))
        digest = hashlib.sha256(
            f"{finding.rule_id}:{':'.join(finding.event_ids)}".encode("utf-8")
        ).hexdigest()[:12]
        return Alert(
            alert_id=f"alert-{digest}",
            timestamp=finding.timestamp,
            rule_id=finding.rule_id,
            risk_type=finding.risk_type,
            user=finding.user,
            ip=finding.ip,
            resource=finding.resource,
            action=finding.action,
            evidence=finding.evidence,
            risk_score=risk_score,
            severity=self.severity(risk_score),
            event_ids=finding.event_ids,
            base_score=base,
        )

    def score_context(self, finding: ContextFinding) -> Alert:
        base = BASE_SCORES[finding.risk_type]
        confidence_points = round(20 * finding.confidence)
        risk_score = min(100, max(0, base + confidence_points + finding.bonus))
        digest = hashlib.sha256(
            f"{finding.signal_id}:{':'.join(finding.event_ids)}".encode("utf-8")
        ).hexdigest()[:12]
        return Alert(
            alert_id=f"alert-{digest}",
            timestamp=finding.timestamp,
            rule_id=finding.signal_id,
            risk_type=finding.risk_type,
            user=finding.user,
            ip=finding.ip,
            resource=finding.resource,
            action=finding.action,
            evidence=finding.evidence,
            risk_score=risk_score,
            severity=self.severity(risk_score),
            event_ids=finding.event_ids,
            base_score=base,
            context_bonus=finding.bonus,
            context_signals=(finding.signal_id,),
            context_evidence=(finding.evidence,),
        )
