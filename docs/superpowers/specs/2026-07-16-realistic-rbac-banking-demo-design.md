# Realistic RBAC Banking Demo Design

## Objective

Replace the current technical-looking RBAC page with a short, realistic banking
operations demo for a lecturer. The demo must make the difference between a
system before and after RBAC visible in a few minutes, while proving that user
creation, authentication, authorization, transaction state, and audit records
are processed by the backend rather than simulated in the browser.

The single demonstration case is a 50,000,000 VND bank transfer:

- Without RBAC, a teller can create and approve the same transaction.
- With RBAC, the teller's approval request is rejected by the backend.
- A controller can approve the pending transaction.

## Demo Journey

Use three independent browser tabs so each actor keeps a real backend session:

1. The administrator signs in, creates `lan.demo`, and assigns the Teller role.
   The Controller demo account is seeded before the presentation.
2. In Baseline mode, `lan.demo` creates a 50,000,000 VND transfer and approves
   it. The product flags that the creator and approver are the same person.
3. The administrator changes the security mode from Baseline to RBAC. The mode
   change is persisted and audited.
4. `lan.demo` creates an equivalent second transfer. The normal approval action
   is no longer part of the teller workspace. In the demo proof panel, the
   presenter deliberately sends the approval request and receives HTTP 403;
   the transaction remains Pending.
5. The seeded controller opens the approval queue and approves the transaction.
   The final timeline shows creation, denied approval, and controller approval.

The Baseline and RBAC comparisons use two separate transaction records. An
already approved baseline transaction is never reverted to manufacture the
second result.

## Product Experience

The visual direction is a professional internal banking operations portal,
called Nova Bank, with role-specific workspaces.

### Routes and workspaces

- `/login` authenticates users and reports backend availability in plain
  language.
- `/transactions` lets tellers create transfers and see their own transfers.
- `/approvals` gives controllers a queue of pending transfers and approval
  details.
- `/admin/users` lets administrators create users and assign one role.
- `/admin/demo-control` lets administrators switch Baseline/RBAC mode and see
  the demo progress.
- `/audit` lets administrators and auditors filter the authorization and
  transaction history.

The navigation only contains work relevant to the signed-in role. The current
role, signed-in user, transaction status, and security mode are always visible.
Baseline mode uses a clear warning banner; RBAC mode uses a protected status
banner.

### Backend proof without weakening the product UI

When RBAC is enabled, tellers do not see an ordinary Approve action. The
transaction detail contains an expandable **Backend protection check** panel
used only by the presentation. It deliberately calls the protected endpoint
and displays the endpoint, HTTP status, required permission, unchanged
transaction state, and matching audit entry.

This panel keeps the normal workflow realistic while allowing the lecturer to
verify that hiding a button is not the security control.

## Authorization Model

Each demonstration user has one role. The existing many-to-many schema may
remain, but the user management UI and creation API assign exactly one role.

| Role | Transactions | Approval | User management | Audit |
| --- | --- | --- | --- | --- |
| Administrator | Read all | None | Create users and assign roles | Read |
| Teller | Create and read own | None | None | None |
| Controller | Read pending and details | Approve | None | None |
| Auditor | Read all | None | None | Read |

Required permissions are:

- `transactions:create`
- `transactions:read_own`
- `transactions:read_all`
- `transactions:approve`
- `users:manage`
- `audit_logs:read`
- `demo:configure`

Baseline mode still requires authentication. It bypasses authorization only for
the demo transaction approval, records the decision as `baseline_bypass`, and
does not bypass user management, audit access, or demo configuration.

RBAC mode checks permissions on every protected request. A denied request must
not mutate the transaction. Transaction approval also validates the current
state, so an already approved transaction returns HTTP 409.

## Backend and Data Flow

Continue using FastAPI and SQLite. Add persisted demo settings and transfer
records without replacing the existing user, role, permission, session, and
audit tables.

A transaction contains exactly these persisted business fields for the demo:

- integer primary key and generated unique transaction reference;
- source account number and destination account number;
- beneficiary name;
- amount in integer VND;
- description;
- `pending` or `approved` status;
- creator user ID and UTC creation timestamp;
- nullable approver user ID and UTC approval timestamp.

Store security mode as either `baseline` or `rbac`. Default reset data uses
Baseline mode, one administrator, one controller, and sample customer/account
data. The administrator-created teller persists when the security mode changes.

The public API additions are:

- `GET /demo/security-mode` returns the active mode to authenticated users.
- `PATCH /demo/security-mode` changes mode and requires `demo:configure`.
- `POST /transactions` creates a pending transaction.
- `GET /transactions` applies role-aware row filtering.
- `GET /transactions/{id}` returns an authorized transaction detail.
- `POST /transactions/{id}/approve` performs the authoritative approval check
  and state transition.
- `GET /transactions/{id}/timeline` returns business and authorization events
  for the transaction.

Mode and transaction data are fetched again when a tab regains focus and before
a sensitive action. Stale frontend state can never override the current backend
policy.

Sessions expire after eight hours. Expiration is checked server-side; logout and
demo reset continue to invalidate tokens immediately.

## Audit Requirements

Every significant event records UTC timestamp, actor, role, resource, action,
outcome, transaction reference where applicable, and a concise detail:

- successful and failed authentication;
- user creation and assigned role;
- security mode changes;
- transaction creation;
- baseline authorization bypass;
- allowed and denied permission decisions;
- successful approval and conflicting repeated approval.

Extend the audit outcome constraint with `baseline_bypass` and `conflict` in
addition to the existing outcomes. Existing development databases are upgraded
at application startup without deleting users or historical audit rows.

The UI presents this as a business timeline on transaction details and as a
filterable technical audit table for administrators and auditors.

## Error and Loading Behavior

- HTTP 401 clears the local session and returns to login with an expired-session
  message.
- HTTP 403 names the missing permission and confirms that data was unchanged.
- HTTP 409 reports that another actor already processed the transaction and
  refreshes its state.
- Validation errors remain beside the affected fields.
- Network failure shows a persistent backend-unavailable banner with Retry; raw
  `Failed to fetch` text is never the primary user message.
- Submit buttons show progress and reject duplicate submission while a request
  is active.

## Implementation Boundaries

Refactor the single large Next.js page into route-level pages, a shared
authenticated shell, reusable transaction and feedback components, and one
central API client. Keep the existing Next.js, FastAPI, SQLite, and UV toolchain.

The project does not need real core-banking integration, funds settlement,
multi-branch data isolation, multi-factor authentication, password recovery, or
production deployment. The security-mode switch is explicitly a presentation
feature and must not be represented as a production capability.

## Verification and Acceptance

Automated API tests must cover:

- administrator creation of a teller with a persisted password and role;
- authenticated Baseline self-approval with a `baseline_bypass` audit record;
- RBAC rejection of the same teller action with HTTP 403 and unchanged state;
- controller approval and a persisted approver identity;
- repeated approval returning HTTP 409;
- teller denial from user management and audit APIs;
- role-aware transaction list filtering;
- server-enforced session expiration;
- all required audit records and transaction timeline ordering.

Frontend verification must cover a successful production build, role-aware
navigation, actionable 401/403/409/network messages, tab-focus refresh, and
disabled duplicate submits.

The manual acceptance run is the five-step journey above. It passes only when
the lecturer can observe two persisted transactions, the denied transaction
remaining Pending, controller approval changing it to Approved, and matching
audit events from the backend.
