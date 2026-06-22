"""Explainable rule-based security event detection."""

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
