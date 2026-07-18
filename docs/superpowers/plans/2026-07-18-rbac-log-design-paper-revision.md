# RBAC and Rule-Based Log Analysis Paper Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the Vietnamese paper with the implemented RBAC Guard solution, centering its design on RBAC and rule-based detection of SQL injection and password guessing.

**Architecture:** Preserve the existing LaTeX section structure. Reframe the narrative around a preventive RBAC model plus an offline, explainable log-analysis pipeline; retain unauthorized-access checking as supporting evidence and context-risk/incident grouping as optional extensions. Treat datasets and artifacts strictly as prototype validation.

**Tech Stack:** LaTeX/pdflatex, Python 3.11 `rbac-guard`, SQLite, TOML configuration, CSV/JSON artifacts.

## Global Constraints

- Do not change `src/`, `tests/`, `data/`, `config/`, application behavior, or demo behavior.
- Do not mention the BankSafe FastAPI/Next.js demo as part of the paper scope.
- Preserve the user-authored deletion of the AI-use statement in `paper/risk_based_access_monitoring/main.tex`.
- Describe SQL injection and password guessing as the two primary detection scenarios.
- Describe `RBAC-UNAUTHORIZED` as supporting authorization evidence only.
- Describe context-risk, scoring, and incident grouping as optional explainable extensions, not ML or real-time adaptive access control.
- Do not claim operational-bank performance, production readiness, or generalization from synthetic datasets.

---

## File structure

- `paper/risk_based_access_monitoring/main.tex`: title only; retains the existing section inclusion order and user change.
- `paper/risk_based_access_monitoring/sections/00_abstract.tex`: concise solution-focused abstract.
- `paper/risk_based_access_monitoring/sections/01_introduction.tex`: problem, contributions, and research questions.
- `paper/risk_based_access_monitoring/sections/03_system_model.tex`: scope, trust boundary, architecture, and data model.
- `paper/risk_based_access_monitoring/sections/04_methodology.tex`: RBAC predicate and detection/extension logic.
- `paper/risk_based_access_monitoring/sections/05_implementation.tex`: short implementation-to-design mapping and reproduction interface.
- `paper/risk_based_access_monitoring/sections/06_evaluation.tex`: prototype validation with correct artifact counts.
- `paper/risk_based_access_monitoring/sections/07_discussion.tex`: design trade-offs and validity limits.
- `paper/risk_based_access_monitoring/sections/08_conclusion.tex`: solution-focused conclusion.
- `paper/risk_based_access_monitoring/tables/*.tex`: retain only tables that substantiate prototype validation; revise captions/wording when needed.

### Task 1: Reframe the paper's purpose and contribution

**Files:**
- Modify: `paper/risk_based_access_monitoring/main.tex`
- Modify: `paper/risk_based_access_monitoring/sections/00_abstract.tex`
- Modify: `paper/risk_based_access_monitoring/sections/01_introduction.tex`
- Modify: `paper/risk_based_access_monitoring/sections/08_conclusion.tex`

**Consumes:** Approved title and scope in `docs/superpowers/specs/2026-07-18-rbac-log-design-paper-revision.md`.

**Produces:** A consistent research framing in which the model/design is the primary contribution and the prototype is validation.

- [ ] **Step 1: Replace the `\title{...}` in `main.tex`**

Set the title exactly to:

```tex
\title{Thiết kế mô hình RBAC và hệ thống phân tích log dựa trên luật để phát hiện rủi ro SQL Injection và dò đoán mật khẩu trong ngân hàng}
```

- [ ] **Step 2: Revise the abstract**

State the design objective, RBAC-to-log-analysis relationship, two primary rules, and synthetic/prototype-only validation. Keep `RBAC-UNAUTHORIZED` and context-risk as supporting/optional capabilities. Remove any wording that presents context scoring or incident grouping as the central contribution.

- [ ] **Step 3: Revise introduction, contributions, and RQs**

Use three contributions: RBAC model and integration boundary; deterministic SQL-injection/password-guessing rules with evidence; reproducible prototype validation. Make RQ1 about solution design, RQ2 about translating the two risks into explainable rules, and RQ3 about validation/tracing on synthetic cases.

- [ ] **Step 4: Revise the conclusion**

Lead with the constructed solution and its design characteristics. State the 60-event baseline only as synthetic validation; make deployment/real-data evaluation future work.

- [ ] **Step 5: Review for narrative consistency**

Run:

```bash
rg -n "đóng góp|trọng tâm|SQL injection|đoán mật khẩu|ngữ cảnh|sản xuất|vận hành" \
  paper/risk_based_access_monitoring/main.tex \
  paper/risk_based_access_monitoring/sections/00_abstract.tex \
  paper/risk_based_access_monitoring/sections/01_introduction.tex \
  paper/risk_based_access_monitoring/sections/08_conclusion.tex
```

Expected: the primary emphasis is RBAC plus two rule-based scenarios; no production-performance claim appears.

### Task 2: Align the design model and method with code

**Files:**
- Modify: `paper/risk_based_access_monitoring/sections/03_system_model.tex`
- Modify: `paper/risk_based_access_monitoring/sections/04_methodology.tex`
- Modify: `paper/risk_based_access_monitoring/figures/architecture.tex`
- Modify: `paper/risk_based_access_monitoring/figures/event_alert_incident.tex` only if its labels overemphasize the optional extension.

**Consumes:** `src/rbac_guard/rules.py`, `src/rbac_guard/context.py`, `src/rbac_guard/scoring.py`, `src/rbac_guard/service.py`, and `config/default.toml`.

**Produces:** A model that exactly distinguishes RBAC, the two primary rules, authorization support, and optional contextual processing.

- [ ] **Step 1: Revise scope and architecture prose**

Describe the system as offline post-analysis of structured CSV/JSON logs. State that SQLite RBAC is used both as the proposed authorization model and as a trusted source for checking access/authorization events. Show parser → RBAC-aware rule engine → scoring/reports as the core path; mark the context profiler and incident builder as optional when `--context-risk` is enabled.

- [ ] **Step 2: Make primary rules explicit in methodology**

Document the implemented SQL patterns: tautology, `union select`, stacked query, and SQL comment; one finding is emitted for the first matching pattern. Document password-guessing grouping by `(user, ip)`, failed authentication events, successful-login/gap reset, `failures=5`, and `window_seconds=300` from `config/default.toml`.

- [ ] **Step 3: Bound the supporting and optional mechanisms**

Keep `RBAC-UNAUTHORIZED` as a secondary rule for denied/missing permissions on `access` and `authorization` events. State that context signals, risk score, and incidents provide explainable prioritization only; they do not alter a real-time authorization decision.

- [ ] **Step 4: Reconcile diagrams and captions**

Ensure the architecture figure visually/narratively makes RBAC and rule engine central. Keep the event→alert→incident figure only as an optional-extension illustration and its caption must state that incident grouping is enabled only in context-risk mode.

- [ ] **Step 5: Verify every algorithmic statement against source**

Run:

```bash
rg -n "SQLI-|AUTH-PASSWORD-GUESSING|RBAC-UNAUTHORIZED|_denial_threshold|context-risk|failures|window_seconds" \
  src/rbac_guard/rules.py src/rbac_guard/context.py config/default.toml
```

Expected: all documented names and thresholds appear in source/configuration.

### Task 3: Reduce implementation and focus validation

**Files:**
- Modify: `paper/risk_based_access_monitoring/sections/05_implementation.tex`
- Modify: `paper/risk_based_access_monitoring/sections/06_evaluation.tex`
- Modify: `paper/risk_based_access_monitoring/tables/baseline_results.tex`
- Modify: `paper/risk_based_access_monitoring/tables/dataset_description.tex`
- Modify: `paper/risk_based_access_monitoring/tables/context_findings.tex`
- Modify: `paper/risk_based_access_monitoring/tables/incident_summary.tex`

**Consumes:** `src/rbac_guard/service.py`, `src/rbac_guard/cli.py`, `paper/risk_based_access_monitoring/artifacts/cp3-baseline/`, and `paper/risk_based_access_monitoring/artifacts/cp3-context/`.

**Produces:** A short implementation section and a validation section that reports only evidence supported by reproducible artifacts.

- [ ] **Step 1: Replace long implementation details with a compact design-to-module mapping**

Keep one paragraph mapping parser, `RBACRepository`, detection rules, scoring, reporting, and shared `analyze` service to the design. Keep the CLI commands/interfaces and report types necessary for reproducibility. Remove coverage commands, checkpoint-process narration, and long shell listings; cite the repository file `HUONG_DAN_CHAY_DEMO.md` as the complete runnable procedure.

- [ ] **Step 2: Rename evaluation intent in prose**

Call this section “Kiểm chứng nguyên mẫu” in its opening and explain that the baseline table confirms expected behavior on synthetic, labeled cases. Retain precision/recall/F1 only with the explicit limitation that they measure rule behavior on constructed data.

- [ ] **Step 3: De-emphasize optional context artifacts**

Keep context tables only as a small optional-extension verification, or compress their narrative into one paragraph and one table if layout requires it. Do not let their aggregate counts dominate the section relative to the two primary rules.

- [ ] **Step 4: Reconcile all result values**

Run:

```bash
rg -n "60|20|1\{,\}0000|0\{,\}9667|0\{,\}9825|14|15|10|3" \
  paper/risk_based_access_monitoring/sections/00_abstract.tex \
  paper/risk_based_access_monitoring/sections/06_evaluation.tex \
  paper/risk_based_access_monitoring/sections/08_conclusion.tex \
  paper/risk_based_access_monitoring/tables/*.tex
```

Compare the values with `metrics.json`, `run_metadata.json`, `context_findings.json`, and `incidents.json`; update prose/tables whenever the artifact and text differ.

- [ ] **Step 5: Confirm the implementation section remains short**

Run:

```bash
wc -w paper/risk_based_access_monitoring/sections/05_implementation.tex
```

Expected: materially shorter than the original implementation section while still naming the concrete modules and output artifacts.

### Task 4: Tighten discussion, limitations, and manuscript verification

**Files:**
- Modify: `paper/risk_based_access_monitoring/sections/07_discussion.tex`
- Modify: `paper/risk_based_access_monitoring/sections/02_related_work.tex` only when terminology must be adjusted for the new focus.
- Modify: `paper/risk_based_access_monitoring/README.md` only if its description no longer matches the revised paper.

**Consumes:** All revised manuscript sections and the approved specification.

**Produces:** A paper that makes a bounded design claim and compiles without LaTeX errors.

- [ ] **Step 1: Reframe design trade-offs**

Center explainability, determinism, traceability, and policy/configuration dependence. Explicitly state that regex coverage and `(user, ip)` thresholding can miss evasive variants or distributed attempts.

- [ ] **Step 2: Remove claims outside scope**

Keep operational limitations: no real logs, no integrity/provenance protection, no multi-source correlation, no automatic response, and no real-time PDP. Do not describe the system as a SIEM replacement or a complete zero-trust deployment.

- [ ] **Step 3: Scan for focus drift**

Run:

```bash
rg -n "BankSafe|FastAPI|Next\.js|học máy|thời gian thực|sản xuất|SIEM|zero trust" \
  paper/risk_based_access_monitoring
```

Expected: no BankSafe/FastAPI/Next.js reference; other terms appear only in limitation or future-work context.

- [ ] **Step 4: Compile and check the final diff**

Run:

```bash
latexmk -pdf main.tex
git diff --check -- paper/risk_based_access_monitoring
```

Run from `paper/risk_based_access_monitoring/` for `latexmk`. Expected: PDF builds successfully and `git diff --check` produces no output. If LaTeX tooling is unavailable, report the exact command failure and still run the whitespace check.

- [ ] **Step 5: Confirm user changes were preserved**

Run:

```bash
git diff -- paper/risk_based_access_monitoring/main.tex
```

Expected: the existing removal of the AI-use statement remains removed; the only new main-file content change is the title.
