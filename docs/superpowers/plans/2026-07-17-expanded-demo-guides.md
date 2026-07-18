# Expanded Demo Guides Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand both demo guides with concise, step-local operational and technical explanations.

**Architecture:** Documentation-only change. Add consistent explanatory callouts beside existing commands and UI actions, preserving their execution order and behavior. Nova Bank will explain service lifecycle, independent sessions, reset state, and backend RBAC evidence; RBAC Guard will explain dependency setup, database seeding, pipeline artifacts, context-risk, and Streamlit.

**Tech Stack:** Markdown, uv, FastAPI, Next.js, Streamlit, SQLite

## Global Constraints

- Preserve all current commands, credentials, endpoints, and demo data exactly.
- Write concise Vietnamese for readers already comfortable with technical tooling.
- Place explanations next to the action they explain; do not introduce a separate duplicate walkthrough.
- Do not alter application source code or test behavior.

---

### Task 1: Expand the Nova Bank demo guide

**Files:**
- Modify: `DEMO_RBAC_NOVA_BANK.md`
- Test: Manual documentation consistency review

**Interfaces:**
- Consumes: existing FastAPI command, Next.js command, seeded credentials, five-step RBAC scenario.
- Produces: a self-contained operator guide where each setup or scenario action states its purpose and expected evidence.

- [ ] **Step 1: Add setup and startup explanations**

Add short paragraphs after the backend/frontend installation and startup commands. Explain that `uv sync --extra api` installs the FastAPI extra, `npm install` resolves the locked frontend dependency graph, Uvicorn exposes the real API on port 8000, and Next.js serves the browser client on port 3000. State that `/health` is the prerequisite check before UI login.

- [ ] **Step 2: Explain the clean-state procedure**

Expand section 5 to say that reset rebuilds deterministic seeded data and invalidates the current session; the three independently opened tabs work because `sessionStorage` is tab-scoped. State that `lan.demo` must be absent before presenting so account creation is observable in the persisted backend state.

- [ ] **Step 3: Add evidence-oriented notes to the five demo steps**

For each step, retain the current **Thao tác**, **Kết quả cần thấy**, and **Lời trình bày**, adding one concise note that identifies the backend decision being demonstrated: user/role creation, baseline self-approval, policy switch, deny without state mutation, controller-only approval plus audit trail.

- [ ] **Step 4: Review the document**

Run:

```bash
rg -n "Bạn làm gì|Ý nghĩa|Kết quả cần thấy|Bước [1-5]" DEMO_RBAC_NOVA_BANK.md
```

Expected: all five steps still have an expected-result checkpoint and the new explanations are present without changing commands or credentials.

- [ ] **Step 5: Commit**

```bash
git add DEMO_RBAC_NOVA_BANK.md
git commit -m "docs: clarify Nova Bank demo steps"
```

### Task 2: Expand the RBAC Guard analysis guide

**Files:**
- Modify: `HUONG_DAN_CHAY_DEMO.md`
- Test: Manual documentation consistency review

**Interfaces:**
- Consumes: existing CLI commands, `data/rbac_seed.json`, baseline/context datasets, config TOML and optional Streamlit UI.
- Produces: a reproducible guide that explains input preparation, pipeline stages and generated reports at each checkpoint.

- [ ] **Step 1: Explain environment and baseline setup**

Add concise notes after `uv sync`, `rbac-guard --help`, the optional regression test, `mktemp -d`, and `init-db`. Explain that uv isolates resolved dependencies, the help command checks CLI entry-point availability, `DEMO_DIR` prevents mixing output between runs, and seed data provides the RBAC permission source used by analysis.

- [ ] **Step 2: Explain the baseline pipeline**

For `check-access`, `analyze`, and `evaluate`, add step-local explanations of permission lookup, parsing/rule evaluation/report generation, and comparison with `expected_label`. Beside each artifact inspection command, identify the exact evidence it is intended to validate.

- [ ] **Step 3: Explain context-risk, Streamlit, and cleanup**

Clarify that `--context-risk` retains rule alerts and adds contextual findings plus incident grouping. Explain that Streamlit is an alternate UI over the same analysis flow, and that it needs a separately initialized `demo.db`. At cleanup, reiterate that removal is only safe because `DEMO_DIR` was created with `mktemp -d` in this guide.

- [ ] **Step 4: Review both guides for command fidelity**

Run:

```bash
git diff --check -- DEMO_RBAC_NOVA_BANK.md HUONG_DAN_CHAY_DEMO.md
rg -n "uv sync|init-db|analyze|evaluate|context-risk|streamlit" HUONG_DAN_CHAY_DEMO.md
rg -n "uvicorn|npm run dev|Khôi phục dữ liệu|Phân tách nhiệm vụ" DEMO_RBAC_NOVA_BANK.md
```

Expected: no whitespace errors; every existing command and pivotal demo action remains present.

- [ ] **Step 5: Commit**

```bash
git add HUONG_DAN_CHAY_DEMO.md
git commit -m "docs: clarify RBAC Guard demo workflow"
```
