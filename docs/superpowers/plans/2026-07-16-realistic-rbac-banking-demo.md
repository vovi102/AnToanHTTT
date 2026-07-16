# Realistic RBAC Banking Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a realistic Nova Bank demo where a teller can self-approve a transfer in Baseline mode, is denied by the backend in RBAC mode, and a controller completes the approval.

**Architecture:** Extend the existing SQLite repository and FastAPI application with persisted demo settings, transfers, transaction-aware audit events, and server-enforced session expiry. Replace the single Next.js client page with an authenticated App Router portal whose navigation and workflows are role-specific, while retaining a separate backend-proof control for the deliberate 403 demonstration.

**Tech Stack:** Python 3.11+, UV, FastAPI, Pydantic, SQLite, pytest, Next.js 15, React 19, TypeScript, Vitest, Testing Library.

## Global Constraints

- Keep FastAPI, SQLite, Next.js, and UV; do not add an external database or authentication service.
- Baseline bypass applies only to authenticated transaction approval and must be audited as `baseline_bypass`.
- RBAC denial must leave the transaction in `pending` state.
- Use two transaction records for the before/after comparison; never revert an approved transaction.
- Keep the presentation workflow short enough for a lecturer-facing demonstration lasting a few minutes.
- Do not modify or commit the user-owned untracked file `Khung_dan_y_v3.md`.

---

### Task 1: Persisted transaction, security-mode, audit, and session domain

**Files:**
- Modify: `src/rbac_guard/rbac.py`
- Test: `tests/test_rbac.py`

**Interfaces:**
- Produces: `RBACRepository.security_mode() -> str`
- Produces: `RBACRepository.set_security_mode(mode: str, actor: str) -> None`
- Produces: `RBACRepository.create_transaction(...) -> dict[str, object]`
- Produces: `RBACRepository.list_transactions(username: str, read_all: bool) -> list[dict[str, object]]`
- Produces: `RBACRepository.get_transaction(reference: str, username: str, read_all: bool) -> dict[str, object] | None`
- Produces: `RBACRepository.approve_transaction(reference: str, approver: str) -> dict[str, object]`
- Produces: `RBACRepository.transaction_timeline(reference: str) -> list[dict[str, object]]`
- Produces: server-enforced eight-hour sessions and migration-safe initialization.

- [ ] **Step 1: Write failing repository tests**

Add tests that initialize a temporary repository, assert Baseline is the reset
default, create `lan.demo`, create a pending transfer, verify own/all row
filtering, approve it once, and assert a second approval raises a conflict.
Also freeze or compare UTC time so a manually expired session is rejected.

```python
transaction = repo.create_transaction(
    creator="lan.demo",
    source_account="001100001234",
    destination_account="002200005678",
    beneficiary_name="Lê Bình",
    amount_vnd=50_000_000,
    description="Thanh toán hợp đồng",
)
assert transaction["status"] == "pending"
assert repo.list_transactions("lan.demo", read_all=False)[0]["reference"] == transaction["reference"]
approved = repo.approve_transaction(transaction["reference"], "controller01")
assert approved["status"] == "approved"
with pytest.raises(ValueError, match="already processed"):
    repo.approve_transaction(transaction["reference"], "controller01")
```

- [ ] **Step 2: Run the new repository tests and verify failure**

Run: `UV_CACHE_DIR=.uv-cache uv run pytest tests/test_rbac.py -q`

Expected: failure because security-mode and transaction methods do not exist.

- [ ] **Step 3: Implement schema initialization and non-destructive migration**

Add `demo_settings` and `transactions` tables. Add `role_at_event` and
`transaction_reference` columns to audit records. Rebuild the audit table at
startup when its CHECK constraint does not yet support `baseline_bypass` and
`conflict`, copying all existing rows before renaming the new table.

Use these exact transaction fields:

```sql
id INTEGER PRIMARY KEY,
reference TEXT NOT NULL UNIQUE,
source_account TEXT NOT NULL,
destination_account TEXT NOT NULL,
beneficiary_name TEXT NOT NULL,
amount_vnd INTEGER NOT NULL CHECK (amount_vnd > 0),
description TEXT NOT NULL,
status TEXT NOT NULL CHECK (status IN ('pending', 'approved')),
created_by INTEGER NOT NULL REFERENCES users(id),
created_at TEXT NOT NULL,
approved_by INTEGER REFERENCES users(id),
approved_at TEXT
```

Generate references as `TRX-YYYYMMDD-NNN` by counting transactions created on
the current UTC date inside the same SQLite transaction.

- [ ] **Step 4: Implement repository behavior and session expiry**

Seed `controller01 / Controller@123` with role `controller`; add roles and grants
for Administrator, Teller, Controller, and Auditor. Set session expiry to
`datetime.now(UTC) + timedelta(hours=8)` and reject/delete expired tokens in
`session_user`. Implement row filtering, atomic pending-to-approved updates,
mode persistence, and transaction-aware auditing.

- [ ] **Step 5: Run repository and full Python tests**

Run: `UV_CACHE_DIR=.uv-cache uv run pytest tests/test_rbac.py -q`

Expected: repository tests pass.

Run: `UV_CACHE_DIR=.uv-cache uv run pytest -q`

Expected: all existing and new Python tests pass.

- [ ] **Step 6: Commit the domain slice**

```bash
git add src/rbac_guard/rbac.py tests/test_rbac.py
git commit -m "feat: add banking transaction RBAC domain"
```

### Task 2: FastAPI transaction and demo-policy enforcement

**Files:**
- Modify: `src/rbac_guard/api.py`
- Modify: `tests/test_api.py`

**Interfaces:**
- Consumes: repository interfaces from Task 1.
- Produces: `GET/PATCH /demo/security-mode`.
- Produces: `POST/GET /transactions`, `GET /transactions/{reference}`,
  `POST /transactions/{reference}/approve`, and
  `GET /transactions/{reference}/timeline`.

- [ ] **Step 1: Write failing before/after API journey tests**

Cover this exact sequence in `tests/test_api.py`:

```python
admin = login(client, "admin01", "Admin@123")
created_user = client.post("/users", headers=auth(admin), json={
    "username": "lan.demo", "display_name": "Lan Nguyễn",
    "password": "Lan@1234", "role": "teller",
})
assert created_user.status_code == 201
teller = login(client, "lan.demo", "Lan@1234")
baseline_tx = create_transfer(client, teller)
assert client.post(f"/transactions/{baseline_tx}/approve", headers=auth(teller)).status_code == 200
assert client.patch("/demo/security-mode", headers=auth(admin), json={"mode": "rbac"}).status_code == 200
rbac_tx = create_transfer(client, teller)
denied = client.post(f"/transactions/{rbac_tx}/approve", headers=auth(teller))
assert denied.status_code == 403
assert denied.json()["detail"]["permission"] == "transactions:approve"
controller = login(client, "controller01", "Controller@123")
assert client.post(f"/transactions/{rbac_tx}/approve", headers=auth(controller)).status_code == 200
```

Add focused tests for role-aware lists, unauthorized audit/user access, repeated
approval returning 409, mode configuration requiring Admin, transaction
validation, and ordered timeline events.

- [ ] **Step 2: Run API tests and verify failure**

Run: `UV_CACHE_DIR=.uv-cache uv run pytest tests/test_api.py -q`

Expected: 404 responses for the new endpoints.

- [ ] **Step 3: Add request and response models**

Define `SecurityModeRequest` with `Literal["baseline", "rbac"]` and
`CreateTransactionRequest` with 10–20 digit account numbers, beneficiary name
length 2–80, positive integer VND amount capped at 10,000,000,000, and
description length 3–160.

- [ ] **Step 4: Implement authoritative permission and state checks**

For listing/detail, grant `read_all` to Administrator, Controller, and Auditor;
otherwise require `transactions:read_own` and filter by creator. For approval:

```python
if repository.has_permission(username, "transactions", "approve"):
    outcome = "allowed"
elif repository.security_mode() == "baseline" and "teller" in repository.user_roles(username):
    outcome = "baseline_bypass"
else:
    audit_denial_and_raise_403("transactions:approve")
```

Map repository not-found to 404 and already-processed to 409. Audit the
authorization decision before the business state transition and include the
transaction reference in both records.

- [ ] **Step 5: Run API and full Python tests**

Run: `UV_CACHE_DIR=.uv-cache uv run pytest tests/test_api.py -q`

Expected: all API tests pass.

Run: `UV_CACHE_DIR=.uv-cache uv run pytest -q`

Expected: all Python tests pass without regressions.

- [ ] **Step 6: Commit the API slice**

```bash
git add src/rbac_guard/api.py tests/test_api.py
git commit -m "feat: enforce RBAC banking transaction API"
```

### Task 3: Frontend API, session, role, and feedback foundation

**Files:**
- Modify: `web/package.json`
- Modify: `web/package-lock.json`
- Create: `web/lib/types.ts`
- Create: `web/lib/api.ts`
- Create: `web/lib/access.ts`
- Create: `web/components/AuthProvider.tsx`
- Create: `web/components/Feedback.tsx`
- Create: `web/components/AppShell.tsx`
- Create: `web/tests/access.test.ts`
- Create: `web/vitest.config.ts`

**Interfaces:**
- Produces: shared `User`, `Transaction`, `AuditEvent`, `SecurityMode`, and
  `ApiError` types.
- Produces: `apiRequest<T>(path, token, options) -> Promise<T>`.
- Produces: `AuthProvider` and `useAuth()` with `user`, `token`, `login`,
  `logout`, and session-expiry behavior.
- Produces: `navigationFor(roles: string[])` for role-aware navigation.

- [ ] **Step 1: Add frontend test dependencies and failing access tests**

Install Vitest and jsdom through npm, add `"test": "vitest run"`, then test
that Teller only receives Transactions, Controller receives Approvals, and
Administrator receives Users, Demo Control, and Audit navigation items.

Run: `cd web && npm test`

Expected: failure because `navigationFor` does not exist.

- [ ] **Step 2: Implement shared types and role navigation**

Use role identifiers `administrator`, `teller`, `controller`, and `auditor`.
Keep permission decisions on the server; `navigationFor` only shapes the user
experience.

- [ ] **Step 3: Implement the API client and authentication provider**

Centralize JSON parsing and convert network failures to `ApiError(0,
"Không thể kết nối máy chủ")`. On 401, clear `novabank_token`, clear user state,
and navigate to `/login?reason=expired`. Keep tokens in `sessionStorage` so
three tabs can hold three independent actors.

- [ ] **Step 4: Implement shared shell and feedback components**

`AppShell` renders Nova Bank branding, actor/role, role-aware navigation,
security-mode banner, and logout. `Feedback` renders success, 403 proof, 409,
and network states with endpoint/status details only when supplied.

- [ ] **Step 5: Run frontend unit tests and type/build checks**

Run: `cd web && npm test`

Expected: access tests pass.

Run: `cd web && npm run build`

Expected: Next.js production build succeeds.

- [ ] **Step 6: Commit the frontend foundation**

```bash
git add web/package.json web/package-lock.json web/lib web/components web/tests web/vitest.config.ts
git commit -m "refactor: add Nova Bank portal foundation"
```

### Task 4: Role-specific Next.js banking workflows

**Files:**
- Modify: `web/app/layout.tsx`
- Replace: `web/app/page.tsx`
- Replace: `web/app/globals.css`
- Create: `web/app/login/page.tsx`
- Create: `web/app/(portal)/layout.tsx`
- Create: `web/app/(portal)/transactions/page.tsx`
- Create: `web/app/(portal)/approvals/page.tsx`
- Create: `web/app/(portal)/admin/users/page.tsx`
- Create: `web/app/(portal)/admin/demo-control/page.tsx`
- Create: `web/app/(portal)/audit/page.tsx`
- Create: `web/components/TransactionForm.tsx`
- Create: `web/components/TransactionList.tsx`
- Create: `web/components/BackendProof.tsx`

**Interfaces:**
- Consumes: API/auth/access foundation from Task 3 and all Task 2 endpoints.
- Produces: complete lecturer-facing five-step demo journey.

- [ ] **Step 1: Build login and authenticated routing**

Make `/` redirect to `/transactions` when authenticated and `/login` otherwise.
The login screen includes the seeded Admin and Controller credentials as demo
helpers, but still submits the typed credentials to FastAPI. Show a backend
health/retry message rather than raw fetch errors.

- [ ] **Step 2: Build Admin user creation and demo-control pages**

User creation requires display name, username, temporary password, and one
role. Demo Control displays Baseline/RBAC comparison steps, the active mode,
and a confirmation before mode change. It never resets users when changing
mode.

- [ ] **Step 3: Build Teller transaction workflow**

The transfer form uses source account, destination account, beneficiary,
integer VND amount, and description. Render transaction reference, amount,
status, creator, and timeline. In Baseline mode show ordinary Self approve; in
RBAC mode remove that action and show the collapsed Backend protection check.
The proof panel sends the real approval request and confirms HTTP 403 plus the
unchanged Pending state.

- [ ] **Step 4: Build Controller approval queue**

Show pending transactions with business details and a confirmation action.
Disable the button while submitting. On HTTP 409, refresh the row and explain
that another actor processed it. Successful approval updates status and actor.

- [ ] **Step 5: Build filtered audit workspace and responsive styling**

Add outcome, actor, transaction-reference, and free-text filters in the client
over the latest backend records. Use the approved navy/blue internal-portal
visual direction, clear Baseline/RBAC banners, desktop sidebar, mobile header,
consistent empty/loading/error states, and no external font dependency.

- [ ] **Step 6: Verify frontend behavior**

Run: `cd web && npm test && npm run build`

Expected: unit tests and Next.js production build pass.

Run the portal against FastAPI and verify each role lands on its allowed
workspace, no ordinary teller approval is visible in RBAC mode, and the proof
panel receives a real 403.

- [ ] **Step 7: Commit the role workflows**

```bash
git add web/app web/components
git commit -m "feat: build realistic Nova Bank RBAC journey"
```

### Task 5: Demo documentation and final verification

**Files:**
- Modify: `README.md`
- Modify: `HUONG_DAN_CHAY_DEMO.md`
- Modify: `docs/USER_JOURNEY_DEMO_RBAC.md`
- Modify: `docs/CHUAN_BI_DEMO_RBAC.md`

**Interfaces:**
- Consumes: final credentials, routes, API behavior, and commands from Tasks 1–4.
- Produces: a reproducible three-tab lecturer demo and recovery checklist.

- [ ] **Step 1: Rewrite the demo journey**

Document the exact actors and credentials:

```text
Admin:      admin01 / Admin@123
Controller: controller01 / Controller@123
Teller:     lan.demo / Lan@1234 (created live)
```

Describe the two 50,000,000 VND transfers, expected status changes, expected
HTTP 403 proof, and the short narration for each step.

- [ ] **Step 2: Update preparation and troubleshooting**

Keep the two-terminal UV/npm startup flow, `/health` check, `.next` cache
recovery, port conflict help, and backend-unavailable behavior. Add three-tab
preparation and a final `POST /demo/reset`/UI reset instruction.

- [ ] **Step 3: Run all verification gates**

Run: `UV_CACHE_DIR=.uv-cache uv run pytest -q`

Expected: all Python tests pass.

Run: `cd web && npm test && npm run build`

Expected: frontend tests and production build pass.

Run: `git diff --check`

Expected: no whitespace errors.

- [ ] **Step 4: Perform the manual acceptance journey**

Start FastAPI on port 8000 and Next.js on port 3000. Use independent tabs for
Admin, Teller, and Controller. Confirm the baseline record is Approved by the
teller, the RBAC record remains Pending after the deliberate 403, the
controller changes it to Approved, and audit entries match all actions.

- [ ] **Step 5: Commit documentation and any verification fixes**

```bash
git add README.md HUONG_DAN_CHAY_DEMO.md docs/USER_JOURNEY_DEMO_RBAC.md docs/CHUAN_BI_DEMO_RBAC.md
git commit -m "docs: update realistic RBAC demo journey"
```
