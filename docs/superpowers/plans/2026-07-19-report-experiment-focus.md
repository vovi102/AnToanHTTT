# Experiment-Focused Report Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove software-testing discussion from the technical report while preserving the experimental design, quantitative evidence, limitations, and reproducibility instructions.

**Architecture:** Treat Chapter 6 as an empirical evaluation chapter rather than a test chapter. Apply terminology consistently across overview, foundations, threat model, controls, implementation, evaluation, and conclusion; retain the existing LaTeX file boundary and label so cross-references remain stable.

**Tech Stack:** LaTeX, `latexmk`, Ripgrep, Poppler `pdfinfo`.

## Global Constraints

- Do not remove dataset descriptions, precision/recall/F1 results, sensitivity analysis, validity threats, or reproducibility commands.
- Do not describe unit tests, integration tests, coverage, Vitest, or production-build checks in the report body.
- Describe Nova Bank audit-to-alert verification as an end-to-end data-flow experiment.
- Keep `chap:verification` and `chapters/06-verification.tex` unchanged as internal identifiers to avoid unnecessary reference churn.

---

### Task 1: Reframe the report around empirical evaluation

**Files:**
- Modify: `report/technical-report/chapters/01-overview.tex`
- Modify: `report/technical-report/chapters/02-foundations.tex`
- Modify: `report/technical-report/chapters/02-threat-model.tex`
- Modify: `report/technical-report/chapters/03-security-controls.tex`
- Modify: `report/technical-report/chapters/05-implementation.tex`
- Modify: `report/technical-report/chapters/06-verification.tex`
- Modify: `report/technical-report/chapters/07-conclusion.tex`

**Interfaces:**
- Consumes: Existing architecture, dataset, metric, and experiment descriptions.
- Produces: A report body that discusses empirical evidence without presenting software-test tooling or test-suite implementation.

- [ ] **Step 1: Capture the current prohibited terminology**

Run:

```bash
rg -n -i 'kiểm thử|unit test|integration test|pytest|coverage|vitest|production build' report/technical-report/chapters -g '*.tex'
```

Expected: Matches in Chapters 1, 2, 3, 5, 6, and 7, including the Chapter 6 title and the Python/frontend test paragraph.

- [ ] **Step 2: Rewrite the evaluation chapter**

In `chapters/06-verification.tex`:

- change `\chapter{Kiểm thử và kết quả}` to `\chapter{Thực nghiệm và đánh giá}`;
- change the first section to `\section{Câu hỏi đánh giá}`;
- retain the RQ1--RQ4 paragraph;
- delete the paragraph beginning `Bộ test Python bao phủ` and its `lstlisting` containing `pytest` and `npm test`;
- rewrite RQ4 as an end-to-end experiment that creates audit records, exports them through the adapter, parses them, and observes password-guessing and unauthorized-access alerts;
- replace the final validity statement so it says regression evidence and the end-to-end experiment support a reproducible PoC, without calling either an integration test.

- [ ] **Step 3: Rewrite cross-chapter testing terminology**

Apply these semantic replacements:

- Chapter 1: describe the adapter contribution as an end-to-end audit-to-alert flow; change completion evidence to automated checks, empirical scenarios, or demonstration scenarios.
- Chapter 2 foundations: replace “dễ viết test/dễ kiểm thử” with “dễ đối chiếu bằng chứng/dễ xác minh hành vi”.
- Threat model: describe criteria as observable evaluation conditions, not test conditions.
- Security controls: describe the audit experiment and state the local audit trail is suitable for demonstrating accountability rather than testing it.
- Implementation: remove `pytest` and `coverage` from technology choices; rename the integration-test section to `Thực nghiệm luồng Nova Bank--pipeline` and describe the executed data flow rather than test code.
- Conclusion: replace the integration-test claim with evidence from the audit-to-alert experiment.

- [ ] **Step 4: Confirm prohibited implementation-testing discussion is gone**

Run:

```bash
rg -n -i 'unit test|integration test|pytest|coverage|vitest|production build|\\chapter\{Kiểm thử' report/technical-report/chapters -g '*.tex'
```

Expected: No output. The generic phrase `significance test` may remain because it denotes statistical hypothesis testing, not software testing.

- [ ] **Step 5: Review the retained evidence**

Run:

```bash
rg -n 'Regression|Holdout|Precision|Recall|F1|Đe dọa tới tính hợp lệ|Tái lập số liệu|RQ[1-4]' report/technical-report/chapters/06-verification.tex
```

Expected: Matches for all four RQs, regression and holdout results, metrics, validity threats, and reproducibility.

- [ ] **Step 6: Commit the editorial revision**

```bash
git add report/technical-report/chapters
git commit -m "docs: focus report on empirical evaluation"
```

Expected: One commit containing only the report chapter edits.

---

### Task 2: Compile and validate the revised PDF

**Files:**
- Verify: `report/technical-report/main.tex`
- Generated, ignored: `report/technical-report/main.pdf`

**Interfaces:**
- Consumes: The revised chapter sources from Task 1.
- Produces: A compiled PDF whose table of contents uses `Thực nghiệm và đánh giá` and whose references remain resolved.

- [ ] **Step 1: Compile from a clean LaTeX dependency graph**

Run:

```bash
cd report/technical-report
latexmk -C
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Expected: Exit code 0 and a new `main.pdf`.

- [ ] **Step 2: Inspect structural compiler warnings**

Run:

```bash
rg -n 'Overfull|undefined references|Citation.*undefined|Reference.*undefined' main.log
```

Expected: No output.

- [ ] **Step 3: Verify the PDF and rendered chapter title**

Run:

```bash
pdfinfo main.pdf | rg 'Pages|Page size'
pdftotext main.pdf - | rg -n 'Thực nghiệm và đánh giá|Kiểm thử và kết quả'
```

Expected: A4 page size, a nonzero page count, at least one `Thực nghiệm và đánh giá` match, and no `Kiểm thử và kết quả` match.

- [ ] **Step 4: Check repository cleanliness and source formatting**

Run:

```bash
git diff --check
git status --short --branch
```

Expected: No whitespace errors; only the plan file may remain uncommitted before the final plan commit.

- [ ] **Step 5: Commit the implementation plan**

```bash
git add docs/superpowers/plans/2026-07-19-report-experiment-focus.md
git commit -m "docs: add experiment-focused report plan"
```

Expected: The plan is committed and the worktree is clean.
