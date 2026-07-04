# Risk-Based Access Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional context-aware access risk analysis that produces context findings and incident reports without changing the default rule-based analysis behavior.

**Architecture:** Keep `service.py` as the orchestrator and add a focused `context.py` module for behavior profiling, context findings, and incident grouping. Extend `config.py`, `models.py`, `scoring.py`, `reporting.py`, `cli.py`, and `web.py` only at their existing boundaries.

**Tech Stack:** Python 3.11, dataclasses, SQLite RBAC repository, argparse CLI, pytest, Streamlit optional UI.

---

### Task 1: Context Models and Config

**Files:**
- Modify: `src/rbac_guard/models.py`
- Modify: `src/rbac_guard/config.py`
- Modify: `config/default.toml`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing config tests**

Add tests that load `[context]` values and reject invalid business hours.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_config.py -q`
Expected: fails because `AppConfig` has no context fields.

- [ ] **Step 3: Implement config and model dataclasses**

Add context fields to `AppConfig` and add `ContextFinding`, `Incident`, and optional context fields on `Alert`.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_config.py -q`
Expected: pass.

### Task 2: Behavior Profiler

**Files:**
- Create: `src/rbac_guard/context.py`
- Test: `tests/test_context.py`

- [ ] **Step 1: Write failing profiler tests**

Cover new IP, after-hours, rare resource, repeated denials, and score bonus caps using real `Event` instances.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_context.py -q`
Expected: import or assertion failure because `context.py` does not exist.

- [ ] **Step 3: Implement minimal profiler**

Create `BehaviorProfiler.analyze(events)` returning deterministic `ContextFinding` values sorted by timestamp and signal ID.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_context.py -q`
Expected: pass.

### Task 3: Context Scoring and Incident Grouping

**Files:**
- Modify: `src/rbac_guard/context.py`
- Modify: `src/rbac_guard/scoring.py`
- Test: `tests/test_context.py`
- Test: `tests/test_scoring.py`

- [ ] **Step 1: Write failing scoring and grouping tests**

Verify context findings convert to alerts, context bonuses are reflected, scores cap at 100, and related alerts group into incidents by user/IP/window.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_context.py tests/test_scoring.py -q`
Expected: fail because scoring and incident grouping are missing.

- [ ] **Step 3: Implement context alert scoring and incident builder**

Extend `RiskScorer` with `score_context()` and add `build_incidents(alerts, window_seconds, scorer)` in `context.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_context.py tests/test_scoring.py -q`
Expected: pass.

### Task 4: Service, Reporting, and CLI Integration

**Files:**
- Modify: `src/rbac_guard/service.py`
- Modify: `src/rbac_guard/reporting.py`
- Modify: `src/rbac_guard/cli.py`
- Test: `tests/test_service.py`
- Test: `tests/test_reporting.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing integration tests**

Verify `analyze(..., context_risk=True)` writes `context_findings.json`, `incidents.csv`, and `incidents.json`; verify CLI supports `--context-risk`; verify default mode does not write incident artifacts.

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_service.py tests/test_reporting.py tests/test_cli.py -q`
Expected: fail because context integration is absent.

- [ ] **Step 3: Implement service and artifact writing**

Add optional `context_risk` parameter, write new artifacts only when enabled, and add CLI flag.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_service.py tests/test_reporting.py tests/test_cli.py -q`
Expected: pass.

### Task 5: Demo Dataset, Web Helpers, and Docs

**Files:**
- Add: `data/logs_risk_demo.csv`
- Modify: `src/rbac_guard/web.py`
- Modify: `README.md`
- Test: `tests/test_web_helpers.py`

- [ ] **Step 1: Write failing web helper test**

Verify incident rows can be filtered by user, severity, risk type, and context signal.

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_web_helpers.py -q`
Expected: fail because incident helper is missing.

- [ ] **Step 3: Implement web helper and update demo/docs**

Add context toggle plumbing in UI, incident helper functions, risk demo dataset, and README commands.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_web_helpers.py -q`
Expected: pass.

### Task 6: Full Verification

**Files:**
- All changed files.

- [ ] **Step 1: Run full test suite**

Run: `.venv/bin/pytest -q`
Expected: all tests pass.

- [ ] **Step 2: Run quality gate**

Run: `.venv/bin/pytest -q --cov=rbac_guard --cov-report=term-missing --cov-fail-under=85`
Expected: coverage gate passes.

- [ ] **Step 3: Run demo CLI smoke**

Run the init-db and context analyze commands on `data/logs_risk_demo.csv`.
Expected: command exits 0 and creates alert, context finding, and incident artifacts.
