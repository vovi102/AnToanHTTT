"""Context-aware behavior profiling and incident helpers."""

from collections import defaultdict, deque
import hashlib

from rbac_guard.config import AppConfig
from rbac_guard.models import Alert, ContextFinding, Event, Incident
from rbac_guard.scoring import RiskScorer


class BehaviorProfiler:
    """Derive explainable context signals from ordered security events."""

    _denial_threshold = 3

    def __init__(self, config: AppConfig):
        self.config = config

    def analyze(self, events: tuple[Event, ...]) -> tuple[ContextFinding, ...]:
        known_ips: dict[str, set[str]] = defaultdict(set)
        known_resources: dict[str, set[str]] = defaultdict(set)
        denials: dict[tuple[str | None, str], deque[Event]] = defaultdict(deque)
        findings: list[ContextFinding] = []

        for event in sorted(events, key=lambda item: item.timestamp):
            findings.extend(self._after_hours(event))
            if event.user is not None:
                findings.extend(self._new_ip(event, known_ips[event.user]))
                findings.extend(self._rare_resource(event, known_resources[event.user]))
            findings.extend(self._repeated_denial(event, denials[(event.user, event.ip)]))
            self._learn_baseline(event, known_ips, known_resources)

        return tuple(sorted(findings, key=lambda item: (item.timestamp, item.signal_id)))

    def _after_hours(self, event: Event) -> tuple[ContextFinding, ...]:
        hour = event.timestamp.hour
        if self.config.business_start_hour <= hour < self.config.business_end_hour:
            return ()
        return (
            self._finding(
                "CTX-AFTER-HOURS",
                event,
                f"after_hours=true; hour={hour}; "
                f"business_hours={self.config.business_start_hour:02d}:00-"
                f"{self.config.business_end_hour:02d}:00",
                self.config.after_hours_bonus,
                0.75,
            ),
        )

    def _new_ip(self, event: Event, known_ips: set[str]) -> tuple[ContextFinding, ...]:
        if not known_ips or event.ip in known_ips:
            return ()
        return (
            self._finding(
                "CTX-NEW-IP",
                event,
                f"new_ip_for_user=true; user={event.user}; ip={event.ip}",
                self.config.new_ip_bonus,
                0.8,
            ),
        )

    def _rare_resource(
        self, event: Event, known_resources: set[str]
    ) -> tuple[ContextFinding, ...]:
        if event.event_type not in {"access", "authorization"}:
            return ()
        if not known_resources or event.resource in known_resources:
            return ()
        return (
            self._finding(
                "CTX-RARE-RESOURCE",
                event,
                f"rare_resource_for_user=true; user={event.user}; resource={event.resource}",
                self.config.rare_resource_bonus,
                0.7,
            ),
        )

    def _repeated_denial(
        self, event: Event, window: deque[Event]
    ) -> tuple[ContextFinding, ...]:
        if event.status != "denied":
            return ()
        window.append(event)
        while (event.timestamp - window[0].timestamp).total_seconds() > (
            self.config.context_window_seconds
        ):
            window.popleft()
        if len(window) != self._denial_threshold:
            return ()
        return (
            ContextFinding(
                signal_id="CTX-REPEATED-DENIAL",
                risk_type="context_anomaly",
                event_ids=tuple(item.event_id for item in window),
                timestamp=event.timestamp,
                user=event.user,
                ip=event.ip,
                resource=event.resource,
                action=event.action,
                evidence=(
                    f"denials_in_window={len(window)}; "
                    f"window_seconds={self.config.context_window_seconds}"
                ),
                confidence=0.85,
                bonus=self.config.repeated_denial_bonus,
            ),
        )

    def _learn_baseline(
        self,
        event: Event,
        known_ips: dict[str, set[str]],
        known_resources: dict[str, set[str]],
    ) -> None:
        if event.user is None:
            return
        known_ips[event.user].add(event.ip)
        if event.status == "success":
            if event.event_type in {"access", "authorization"}:
                known_resources[event.user].add(event.resource)

    def _finding(
        self,
        signal_id: str,
        event: Event,
        evidence: str,
        bonus: int,
        confidence: float,
    ) -> ContextFinding:
        return ContextFinding(
            signal_id=signal_id,
            risk_type="context_anomaly",
            event_ids=(event.event_id,),
            timestamp=event.timestamp,
            user=event.user,
            ip=event.ip,
            resource=event.resource,
            action=event.action,
            evidence=evidence,
            confidence=confidence,
            bonus=bonus,
        )


def build_incidents(
    alerts: tuple[Alert, ...], window_seconds: int, scorer: RiskScorer
) -> tuple[Incident, ...]:
    """Group related alerts by user/IP and nearby timestamps."""
    grouped: dict[tuple[str | None, str], list[Alert]] = defaultdict(list)
    for alert in sorted(alerts, key=lambda item: item.timestamp):
        grouped[(alert.user, alert.ip)].append(alert)

    incidents: list[Incident] = []
    for group_alerts in grouped.values():
        segment: list[Alert] = []
        for alert in group_alerts:
            gap_exceeded = bool(
                segment
                and (alert.timestamp - segment[-1].timestamp).total_seconds() > window_seconds
            )
            if gap_exceeded:
                incidents.append(_incident_from_segment(segment, scorer))
                segment = []
            segment.append(alert)
        if segment:
            incidents.append(_incident_from_segment(segment, scorer))

    return tuple(sorted(incidents, key=lambda item: (item.start_time, item.incident_id)))


def _incident_from_segment(segment: list[Alert], scorer: RiskScorer) -> Incident:
    event_ids = _ordered_unique(
        event_id for alert in segment for event_id in alert.event_ids
    )
    alert_ids = tuple(alert.alert_id for alert in segment)
    evidence = _ordered_unique(
        item
        for alert in segment
        for item in ((alert.evidence,) + alert.context_evidence)
        if item
    )
    risk_types = tuple(sorted({alert.risk_type for alert in segment}))
    context_signals = _ordered_unique(
        signal for alert in segment for signal in alert.context_signals
    )
    chain_bonus = scorer.config.session_chain_bonus if len(segment) > 1 else 0
    risk_score = min(100, max(alert.risk_score for alert in segment) + chain_bonus)
    digest = hashlib.sha256(":".join(alert_ids).encode("utf-8")).hexdigest()[:12]
    first = segment[0]
    last = segment[-1]
    return Incident(
        incident_id=f"incident-{digest}",
        user=first.user,
        ip=first.ip,
        start_time=first.timestamp,
        end_time=last.timestamp,
        severity=scorer.severity(risk_score),
        risk_score=risk_score,
        risk_types=risk_types,
        context_signals=context_signals,
        event_ids=event_ids,
        alert_ids=alert_ids,
        summary=(
            f"{first.user or 'unknown'} from {first.ip} triggered "
            f"{len(segment)} alerts across {', '.join(risk_types)}"
        ),
        evidence=evidence,
    )


def _ordered_unique(values) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)
