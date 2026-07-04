# Risk-Based Access Monitoring Upgrade Design

## Objective

Upgrade the current RBAC Guard PoC from a simple rule-based detector into a
risk-based access monitoring system. The upgraded system keeps the existing
RBAC, parser, rule detection, scoring, reporting, CLI, and optional Streamlit UI,
but adds behavioral context so alerts explain not only what matched a rule, but
why the event is risky in the user's normal access context.

The revised topic can be presented as:

> Designing a risk-based access monitoring system using RBAC, security log
> analysis, and behavioral context scoring for banking environments.

## Current Baseline

The existing system already supports:

- SQLite RBAC with users, roles, permissions, user-role assignments, and
  role-permission assignments.
- CSV/JSON log parsing into a normalized Event model.
- Rule detection for SQL Injection, password guessing, and unauthorized access.
- Risk scoring into Low, Medium, High, and Critical severities.
- Atomic reporting to CSV/JSON and metadata files.
- Evaluation against expected labels.
- CLI and read-only Streamlit UI that share the application service.

This is a solid PoC, but the current risk model is mostly rule-driven. A higher
quality project should show how RBAC and logs can be combined with behavioral
context to produce more meaningful security triage.

## Proposed Upgrade

Add a Context-Aware Risk Scoring layer with two supporting concepts:

1. Behavior profile: a lightweight baseline derived from historical or earlier
   benign events.
2. Incident timeline: grouping related alerts/events so the output tells a
   short attack story instead of only listing independent alerts.

The upgraded pipeline becomes:

```text
CLI / Streamlit UI
        |
Application Service
        |
Parser
        |
RBAC Checker + Rule Detection
        |
Behavior Profiler
        |
Context Risk Scorer
        |
Incident Reporter
```

## Behavioral Signals

The profiler should compute simple, explainable signals. No machine learning is
required for this upgrade.

### User-IP familiarity

For each user, record previously observed source IPs. A later event from an
unseen IP adds risk, especially when paired with authentication failure,
authorization denial, or sensitive resources.

Example evidence:

```text
new_ip_for_user=true; user=teller01; ip=198.51.100.50
```

### After-hours activity

Treat configurable business hours as the normal operating window. Events outside
that window add risk. The default can be 08:00-18:00 local time.

Example evidence:

```text
after_hours=true; hour=22; business_hours=08:00-18:00
```

### Rare resource access

Track resources normally accessed by a user. Access to a resource not present in
the user's baseline adds risk. This is especially useful when RBAC permits the
action but the behavior is unusual.

Example evidence:

```text
rare_resource_for_user=true; user=auditor01; resource=accounts
```

### Repeated denials

Count RBAC denials or denied log statuses within a sliding window. Repeated
denials suggest probing, even when every single request is blocked.

Example evidence:

```text
denials_in_window=4; window_seconds=300
```

### Session risk chain

Group events by user and IP within a time window. A sequence such as failed
logins, new IP, after-hours access, and denied permission should produce a
stronger incident than any individual event alone.

Example evidence:

```text
chain=failed_login->new_ip->unauthorized_access
```

## Data Model Changes

Extend the normalized analysis output rather than replacing current models.

### ContextFinding

A ContextFinding should include:

- `signal_id`: stable identifier such as `CTX-NEW-IP`.
- `risk_type`: `context_anomaly`.
- `event_ids`: source event IDs.
- `user`, `ip`, `resource`, and `action` where available.
- `confidence`: integer or float in a fixed range.
- `evidence`: concise key-value explanation.

### BehaviorProfile

The profile can be in memory for the PoC. It should include:

- Known IPs per user.
- Known resources per user.
- Counts of failed authentications by user/IP.
- Counts of denied actions by user/IP.
- Business-hours configuration.

The PoC does not need persistent profile storage. Reproducibility is more
important than long-term state.

### Incident

Incident output should include:

- `incident_id`.
- `user`.
- `ip`.
- `start_time`.
- `end_time`.
- `severity`.
- `risk_score`.
- `risk_types`.
- `event_ids`.
- `summary`.
- `evidence`.

Incidents should be derived from alerts and context findings grouped by user/IP
within a configurable time window.

## Scoring Design

Keep the existing base risk scores for SQL Injection, password guessing, and
unauthorized access. Add context bonuses with explicit caps.

Suggested context bonuses:

| Signal | Bonus |
| --- | ---: |
| New IP for user | +10 |
| After-hours activity | +8 |
| Rare resource for user | +8 |
| Repeated denials in window | +12 |
| Multi-signal session chain | +15 |

The final score remains capped at 100. Severity thresholds can stay compatible
with the current config:

- Medium: 30
- High: 60
- Critical: 85

This keeps the old evaluation stable while making high-risk combinations more
visible.

## Demo Dataset Upgrade

Add a second dataset rather than mutating the current one:

```text
data/logs_risk_demo.csv
```

The new dataset should include:

- Normal daytime access from familiar IPs.
- A user logging in from a new IP.
- After-hours access to a sensitive resource.
- A resource access that is RBAC-allowed but unusual for the user.
- Repeated denied access attempts.
- A chained scenario combining failed logins, new IP, and unauthorized access.

The existing `data/logs_demo.csv` remains the baseline rule-detection dataset.

## CLI Behavior

Add an optional mode or flag to the existing `analyze` command:

```bash
rbac-guard analyze \
  --db demo.db \
  --log data/logs_risk_demo.csv \
  --config config/default.toml \
  --output artifacts \
  --context-risk
```

When enabled, analysis should write the existing alert artifacts plus:

```text
incidents.csv
incidents.json
context_findings.json
```

If the flag is not enabled, current behavior should remain unchanged.

## Configuration

Extend `config/default.toml` with explainable defaults:

```toml
[context]
enabled = false
business_start_hour = 8
business_end_hour = 18
window_seconds = 300
new_ip_bonus = 10
after_hours_bonus = 8
rare_resource_bonus = 8
repeated_denial_bonus = 12
session_chain_bonus = 15
```

The CLI flag should override `context.enabled` for demo convenience.

## Web UI Upgrade

The Streamlit UI should stay read-only. Add:

- A toggle for context-aware risk analysis.
- Incident summary table.
- Filters for user, risk type, severity, and context signal.
- Timeline view sorted by event time for selected incident.

This UI change is useful for presentation, but the CLI and tests remain the
primary source of correctness.

## Reporting Changes

Existing alerts should gain optional context fields:

- `context_signals`
- `context_evidence`
- `base_score`
- `context_bonus`

New incident reports should summarize grouped behavior rather than duplicate
every field from alerts.

Example incident summary:

```text
teller01 from 198.51.100.50 had 10 failed login attempts, used a new IP, and
attempted unauthorized users:delete within 5 minutes.
```

## Evaluation Strategy

Keep the current metrics for the three existing risk types. Add a small
scenario-based evaluation for context risk:

- Number of expected incidents.
- Number of detected incidents.
- Whether each expected incident contains the required event IDs.
- Whether severity increased when multiple context signals appeared together.

This avoids pretending the context layer is a fully statistical anomaly detector.

## Testing Requirements

Add focused tests for:

- New IP detection.
- After-hours detection.
- Rare resource detection.
- Repeated denial window behavior.
- Incident grouping by user/IP/time window.
- Context score bonuses and score cap at 100.
- CLI behavior with and without `--context-risk`.
- Reporter creation of incident/context artifacts.

Existing tests should continue passing unchanged.

## Report and Presentation Changes

Update the report narrative:

- Chapter 1: state the upgraded problem as risk-based access monitoring.
- Chapter 3: add behavior profiling and context-aware scoring to the system
  design.
- Chapter 4: describe the new context dataset, CLI flag, and incident output.
- Chapter 5: add scenario-based evaluation for incident detection and context
  scoring.
- Chapter 6: discuss limitations honestly: the profile is rule-based and
  in-memory, not adaptive ML.

The presentation should emphasize:

- RBAC says whether an action is allowed.
- Logs show what actually happened.
- Behavioral context explains why an allowed or blocked action may still be
  risky.
- Incident timelines make the result easier for a security analyst to triage.

## Out of Scope

The upgrade should not add:

- Machine learning.
- Real-time streaming.
- Persistent user behavior database.
- Full SIEM integration.
- Authentication system implementation.
- Real banking data.

These are good future-work items, but including them now would increase risk
without improving the current PoC enough.

## Success Criteria

The upgrade is successful when:

- Existing analysis behavior still works without context mode.
- Context mode produces context findings and incidents on the new demo dataset.
- At least one scenario shows RBAC-allowed access becoming higher risk due to
  context.
- At least one scenario groups multiple events into a clear incident timeline.
- Tests cover the new profiler, scorer, reporter, and CLI paths.
- The report and presentation can clearly explain why the upgraded topic is
  deeper than the original rule-based detector.
