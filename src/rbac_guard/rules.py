"""Explainable rule-based security event detection."""

from collections import defaultdict, deque
import re

from rbac_guard.models import Event, Finding


class SQLInjectionRule:
    """Detect a small explicit set of SQL injection indicators."""

    _patterns = (
        (
            "SQLI-TAUTOLOGY",
            "tautology",
            re.compile(r"(?:['\"]\s*)?\bor\b\s+(?:\d+|'[^']*')\s*(?:=|>)\s*(?:\d+|'[^']*')", re.I),
        ),
        ("SQLI-UNION", "union-select", re.compile(r"\bunion\s+select\b", re.I)),
        (
            "SQLI-STACKED",
            "stacked-query",
            re.compile(r";\s*(?:drop|delete|insert|update|select)\b", re.I),
        ),
        ("SQLI-COMMENT", "sql-comment", re.compile(r"['\"]\s*(?:--|#)", re.I)),
    )

    def evaluate(self, events: tuple[Event, ...]) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        for event in events:
            for rule_id, pattern_name, pattern in self._patterns:
                if pattern.search(event.request):
                    excerpt = event.request[:160]
                    findings.append(
                        Finding(
                            rule_id=rule_id,
                            risk_type="sql_injection",
                            event_ids=(event.event_id,),
                            timestamp=event.timestamp,
                            user=event.user,
                            ip=event.ip,
                            resource=event.resource,
                            action=event.action,
                            evidence=f"pattern={pattern_name}; request={excerpt}",
                            confidence=0.95,
                        )
                    )
                    break
        return tuple(findings)


class PasswordGuessingRule:
    """Detect repeated failed logins for the same user and source IP."""

    def __init__(self, failures: int, window_seconds: int):
        self.failures = failures
        self.window_seconds = window_seconds

    def _finding_for_segment(self, segment: list[Event]) -> Finding | None:
        window: deque[Event] = deque()
        threshold_reached = False
        for event in segment:
            window.append(event)
            while (event.timestamp - window[0].timestamp).total_seconds() > self.window_seconds:
                window.popleft()
            if len(window) >= self.failures:
                threshold_reached = True
                break
        if not threshold_reached:
            return None

        last = segment[-1]
        first = segment[0]
        return Finding(
            rule_id="AUTH-PASSWORD-GUESSING",
            risk_type="password_guessing",
            event_ids=tuple(event.event_id for event in segment),
            timestamp=last.timestamp,
            user=last.user,
            ip=last.ip,
            resource=last.resource,
            action=last.action,
            evidence=(
                f"count={len(segment)}; first={first.timestamp.isoformat()}; "
                f"last={last.timestamp.isoformat()}; user={last.user}; ip={last.ip}"
            ),
            confidence=min(1.0, 0.8 + max(0, len(segment) - self.failures) * 0.02),
            repeat_count=len(segment),
        )

    def evaluate(self, events: tuple[Event, ...]) -> tuple[Finding, ...]:
        groups: dict[tuple[str | None, str], list[Event]] = defaultdict(list)
        for event in sorted(events, key=lambda item: item.timestamp):
            if event.event_type == "authentication":
                groups[(event.user, event.ip)].append(event)

        findings: list[Finding] = []
        for group in groups.values():
            segment: list[Event] = []
            for event in group:
                gap_exceeded = bool(
                    segment
                    and (event.timestamp - segment[-1].timestamp).total_seconds()
                    > self.window_seconds
                )
                if event.status == "success" or gap_exceeded:
                    finding = self._finding_for_segment(segment)
                    if finding is not None:
                        findings.append(finding)
                    segment = []
                if event.status == "failed":
                    segment.append(event)
            finding = self._finding_for_segment(segment)
            if finding is not None:
                findings.append(finding)

        return tuple(sorted(findings, key=lambda item: (item.timestamp, item.rule_id)))
