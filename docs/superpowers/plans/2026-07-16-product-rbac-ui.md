# Product-like RBAC Portal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Biến Nova Bank thành giao diện sản phẩm dễ đọc, không lộ hướng dẫn/API, đồng thời chứng minh RBAC bằng một trang phê duyệt bị backend từ chối.

**Architecture:** FastAPI bổ sung một resource đọc hồ sơ phê duyệt dùng chung quyết định quyền với POST approval và ghi audit trước khi trả 403. Next.js thay panel proof bằng route `/approvals/[reference]`, dùng helper presentation để dịch mode/audit sang ngôn ngữ nghiệp vụ, rồi áp dụng typography Inter/Segoe UI tối thiểu 14px trên toàn portal.

**Tech Stack:** Python 3.11+, FastAPI, SQLite, pytest, Next.js 15, React 19, TypeScript, Vitest, CSS.

## Global Constraints

- Font stack duy nhất: `Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
- Không tải font từ mạng; không dùng Georgia hoặc Times New Roman.
- Mọi `font-size` hiển thị trong portal tối thiểu 14px; body 16px.
- UI không hiển thị FastAPI URL, health URL, endpoint, HTTP status, permission, SQLite, hướng dẫn demo hoặc kịch bản.
- Không quyết định quyền ở frontend; API luôn xác minh session và permission.
- Teller ở RBAC không được đọc hồ sơ phê duyệt dù biết reference.
- Giữ nguyên role, permission, tài khoản seed, schema giao dịch, Streamlit, CLI, paper/report và dữ liệu thực nghiệm.
- Không sửa hoặc commit file người dùng `Khung_dan_y_v3.md`.

---

### Task 1: Bảo vệ resource hồ sơ phê duyệt tại backend

**Files:**
- Modify: `tests/test_api.py`
- Modify: `src/rbac_guard/api.py`

**Interfaces:**
- Consumes: `repository.has_permission(username, "transactions", "approve")`, `repository.security_mode()`, `repository.user_roles(username)`, `repository.audit(...)`.
- Produces: `GET /approvals/{reference}` và helper `enforce_approval_policy(reference, user, action) -> str` dùng cho cả GET và POST.

- [ ] **Step 1: Viết test API thất bại cho access resource và audit**

Thêm vào `tests/test_api.py`:

```python
def test_approval_resource_is_protected_and_audited(client: TestClient) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    created = client.post(
        "/users",
        headers=auth(admin_token),
        json={
            "username": "lan.demo",
            "display_name": "Lan Nguyễn",
            "password": "Lan@1234",
            "role": "teller",
        },
    )
    assert created.status_code == 201
    teller_token = login(client, "lan.demo", "Lan@1234")
    reference = create_transfer(client, teller_token)

    baseline_view = client.get(
        f"/approvals/{reference}", headers=auth(teller_token)
    )
    assert baseline_view.status_code == 200
    assert baseline_view.json()["reference"] == reference

    changed = client.patch(
        "/demo/security-mode",
        headers=auth(admin_token),
        json={"mode": "rbac"},
    )
    assert changed.status_code == 200

    denied = client.get(f"/approvals/{reference}", headers=auth(teller_token))
    assert denied.status_code == 403
    unchanged = client.get(
        f"/transactions/{reference}", headers=auth(teller_token)
    )
    assert unchanged.json()["status"] == "pending"

    controller_token = login(client, "controller01", "Controller@123")
    allowed = client.get(
        f"/approvals/{reference}", headers=auth(controller_token)
    )
    assert allowed.status_code == 200
    assert allowed.json()["reference"] == reference
    assert client.get(
        "/approvals/TXN-DOES-NOT-EXIST", headers=auth(controller_token)
    ).status_code == 404
    assert client.get(
        "/approvals/TXN-DOES-NOT-EXIST", headers=auth(teller_token)
    ).status_code == 403

    logs = client.get("/audit-logs", headers=auth(admin_token)).json()
    review_outcomes = [
        event["outcome"]
        for event in logs
        if event["transaction_reference"] == reference
        and event["resource"] == "transactions"
        and event["action"] == "review"
    ]
    assert "baseline_bypass" in review_outcomes
    assert "denied" in review_outcomes
    assert "allowed" in review_outcomes
```

- [ ] **Step 2: Chạy test để xác nhận RED**

Run:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest tests/test_api.py::test_approval_resource_is_protected_and_audited -q
```

Expected: FAIL vì `GET /approvals/{reference}` trả 404.

- [ ] **Step 3: Tách quyết định quyền dùng chung**

Trong `src/rbac_guard/api.py`, thêm trước các approval route:

```python
def approval_policy_outcome(user: dict[str, str]) -> str:
    username = user["username"]
    if repository.has_permission(username, "transactions", "approve"):
        return "allowed"
    if (
        repository.security_mode() == "baseline"
        and "teller" in repository.user_roles(username)
    ):
        return "baseline_bypass"
    return "denied"


def enforce_approval_policy(
    reference: str, user: dict[str, str], action: str
) -> str:
    outcome = approval_policy_outcome(user)
    details = {
        "allowed": "Approval policy allowed the operation",
        "baseline_bypass": "Basic control policy bypassed separation of duties",
        "denied": "Separation of duties denied the operation",
    }
    repository.audit(
        user["username"],
        "transactions",
        action,
        outcome,
        details[outcome],
        transaction_reference=reference,
    )
    if outcome == "denied":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Bạn không có quyền phê duyệt giao dịch này",
                "permission": "transactions:approve",
            },
        )
    return outcome
```

Helper phải đánh giá permission trước khi đọc reference để người không có quyền
luôn nhận 403, kể cả khi reference không tồn tại.

- [ ] **Step 4: Thêm GET resource và dùng helper trong POST**

Thêm route:

```python
@app.get("/approvals/{reference}")
def approval_detail(reference: str, user: CurrentUser) -> dict[str, object]:
    enforce_approval_policy(reference, user, "review")
    return readable_transaction(reference, user)
```

Trong `approve_transaction`, thay toàn bộ nhánh permission/baseline/denied hiện
có bằng:

```python
username = user["username"]
enforce_approval_policy(reference, user, "approve")
```

Giữ nguyên `repository.approve_transaction`, xử lý 404, conflict 409 và audit
conflict phía sau.

- [ ] **Step 5: Chạy test mục tiêu và toàn bộ API tests**

Run:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest tests/test_api.py::test_approval_resource_is_protected_and_audited -q
UV_CACHE_DIR=.uv-cache uv run pytest tests/test_api.py -q
```

Expected: cả hai lệnh exit 0; test GET mới và các POST approval cũ đều pass.

- [ ] **Step 6: Commit backend resource**

```bash
git add src/rbac_guard/api.py tests/test_api.py
git commit -m "feat: protect approval detail resource"
```

---

### Task 2: Tạo presentation model bằng ngôn ngữ nghiệp vụ

**Files:**
- Create: `web/lib/presentation.ts`
- Create: `web/tests/presentation.test.ts`
- Modify: `web/lib/transactions.ts`
- Modify: `web/tests/transactions.test.ts`

**Interfaces:**
- Consumes: `SecurityMode`, audit resource/action/outcome và role arrays.
- Produces: `modePresentation(mode)`, `auditOutcomeLabel(outcome)`, `auditActionLabel(resource, action)` và approval presentation `self_approve | approval_link | waiting | none`.

- [ ] **Step 1: Viết failing tests cho nhãn và approval presentation**

Tạo `web/tests/presentation.test.ts`:

```typescript
import { describe, expect, it } from "vitest";

import {
  auditActionLabel,
  auditOutcomeLabel,
  modePresentation,
} from "../lib/presentation";

describe("product presentation copy", () => {
  it("presents security modes in business language", () => {
    expect(modePresentation("baseline").title).toBe("Kiểm soát cơ bản");
    expect(modePresentation("rbac").title).toBe("Phân tách nhiệm vụ");
  });

  it("translates audit outcomes", () => {
    expect(auditOutcomeLabel("baseline_bypass")).toBe("Bỏ qua kiểm soát");
    expect(auditOutcomeLabel("denied")).toBe("Đã từ chối");
    expect(auditOutcomeLabel("allowed")).toBe("Đã cho phép");
    expect(auditOutcomeLabel("success")).toBe("Thành công");
  });

  it("translates audit actions without exposing resource syntax", () => {
    expect(auditActionLabel("transactions", "create")).toBe("Tạo giao dịch");
    expect(auditActionLabel("transactions", "review")).toBe("Xem hồ sơ phê duyệt");
    expect(auditActionLabel("transactions", "approve")).toBe("Phê duyệt giao dịch");
    expect(auditActionLabel("unknown", "unknown")).toBe("Hoạt động hệ thống");
  });
});
```

Trong `web/tests/transactions.test.ts`, thay proof expectation bằng:

```typescript
expect(approvalPresentation("rbac", ["teller"])).toBe("waiting");
expect(approvalPresentation("rbac", ["controller"])).toBe("approval_link");
expect(approvalPresentation("baseline", ["teller"])).toBe("self_approve");
```

- [ ] **Step 2: Chạy Vitest để xác nhận RED**

Run:

```bash
cd web
npm test
```

Expected: FAIL vì `presentation.ts` chưa tồn tại và navigation/presentation vẫn
dùng route/value cũ.

- [ ] **Step 3: Implement presentation helpers**

Tạo `web/lib/presentation.ts`:

```typescript
import type { SecurityMode } from "./types";

const modes: Record<SecurityMode, { title: string; description: string }> = {
  baseline: {
    title: "Kiểm soát cơ bản",
    description: "Giao dịch viên có thể hoàn tất giao dịch trong một bước.",
  },
  rbac: {
    title: "Phân tách nhiệm vụ",
    description: "Giao dịch cần Kiểm soát viên độc lập phê duyệt.",
  },
};

const outcomes: Record<string, string> = {
  allowed: "Đã cho phép",
  denied: "Đã từ chối",
  success: "Thành công",
  failed: "Thất bại",
  baseline_bypass: "Bỏ qua kiểm soát",
  conflict: "Xung đột trạng thái",
};

const actions: Record<string, string> = {
  "transactions:create": "Tạo giao dịch",
  "transactions:read": "Tra cứu giao dịch",
  "transactions:review": "Xem hồ sơ phê duyệt",
  "transactions:approve": "Phê duyệt giao dịch",
  "users:manage": "Quản lý nhân viên",
  "demo:configure": "Cập nhật chính sách phê duyệt",
  "audit_logs:read": "Xem lịch sử hoạt động",
  "session:login": "Đăng nhập",
  "session:logout": "Đăng xuất",
};

export function modePresentation(mode: SecurityMode) {
  return modes[mode];
}

export function auditOutcomeLabel(outcome: string): string {
  return outcomes[outcome] ?? "Không xác định";
}

export function auditActionLabel(resource: string, action: string): string {
  return actions[`${resource}:${action}`] ?? "Hoạt động hệ thống";
}
```

- [ ] **Step 4: Cập nhật approval presentation**

Trong `web/lib/transactions.ts`:

```typescript
export type ApprovalPresentation =
  | "self_approve"
  | "approval_link"
  | "waiting"
  | "none";

export function approvalPresentation(
  mode: SecurityMode,
  roles: string[],
): ApprovalPresentation {
  if (roles.includes("controller")) return "approval_link";
  if (!roles.includes("teller")) return "none";
  return mode === "baseline" ? "self_approve" : "waiting";
}
```

- [ ] **Step 5: Chạy frontend unit tests và commit**

Run:

```bash
cd web
npm test
```

Expected: toàn bộ Vitest pass.

Commit:

```bash
git add web/lib/presentation.ts web/tests/presentation.test.ts web/lib/transactions.ts web/tests/transactions.test.ts
git commit -m "refactor: add product presentation model"
```

---

### Task 3: Thay proof panel bằng approval detail route

**Files:**
- Delete: `web/components/BackendProof.tsx`
- Modify: `web/components/TransactionList.tsx`
- Modify: `web/components/Feedback.tsx`
- Modify: `web/lib/types.ts`
- Modify: `web/app/(portal)/transactions/page.tsx`
- Modify: `web/app/(portal)/approvals/page.tsx`
- Create: `web/app/(portal)/approvals/[reference]/page.tsx`

**Interfaces:**
- Consumes: `GET /approvals/{reference}`, `POST /transactions/{reference}/approve`, `approvalPresentation(...)`.
- Produces: Product route `/approvals/[reference]` với states loading/ready/denied/not_found/error/success; TransactionList không còn proof props.

- [ ] **Step 1: Thu gọn FeedbackState và Feedback**

Trong `web/lib/types.ts`, thay `FeedbackState` bằng:

```typescript
export type FeedbackState = {
  kind: "success" | "error";
  title: string;
  message: string;
};
```

Trong `web/components/Feedback.tsx`, chỉ render `title` và `message`; xóa toàn bộ
`<code>` endpoint/status/permission.

- [ ] **Step 2: Refactor TransactionList thành hành động nghiệp vụ**

Xóa import và render `BackendProof`. Props mới:

```typescript
type TransactionListProps = {
  transactions: Transaction[];
  mode: SecurityMode;
  roles: string[];
  busyReference?: string | null;
  onApprove?: (transaction: Transaction) => void;
};
```

Render theo presentation:

```tsx
{transaction.status === "pending" && presentation === "self_approve" && (
  <div className="baseline-action">
    <p>Giao dịch có thể được hoàn tất theo chính sách hiện tại.</p>
    <button
      className="button warning"
      disabled={busyReference === transaction.reference}
      onClick={() => onApprove?.(transaction)}
    >
      {busyReference === transaction.reference ? "Đang xử lý…" : "Hoàn tất giao dịch"}
    </button>
  </div>
)}
{transaction.status === "pending" && presentation === "approval_link" && (
  <Link className="button primary" href={`/approvals/${transaction.reference}`}>
    Xem và phê duyệt <span>→</span>
  </Link>
)}
{transaction.status === "pending" && presentation === "waiting" && (
  <div className="waiting-approval">Đang chờ Kiểm soát viên phê duyệt</div>
)}
```

Empty state dùng “Chưa phát sinh giao dịch” và không nhắc kịch bản.

- [ ] **Step 3: Xóa proof state khỏi Transactions page**

Trong `web/app/(portal)/transactions/page.tsx`:

- xóa `proof`, `setProof` và toàn bộ `runProof`;
- bỏ `status` khỏi các `FeedbackState` object;
- message tạo thành công là
  ```${created.reference} đã được ghi nhận và đang chờ xử lý.```;
- gọi TransactionList chỉ với:

```tsx
<TransactionList
  transactions={transactions}
  mode={mode}
  roles={user?.roles ?? []}
  busyReference={busy}
  onApprove={approve}
/>
```

- [ ] **Step 4: Đổi Controller queue sang link detail**

Trong `web/app/(portal)/approvals/page.tsx`, xóa `busy`, `approve`, confirm và
POST. Render:

```tsx
<TransactionList
  transactions={pending}
  mode="rbac"
  roles={user?.roles ?? []}
/>
```

- [ ] **Step 5: Tạo approval detail page với access state**

Tạo `web/app/(portal)/approvals/[reference]/page.tsx` với nội dung hoàn chỉnh:

```tsx
"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "../../../../components/AuthProvider";
import { Feedback } from "../../../../components/Feedback";
import { ApiError } from "../../../../lib/api";
import { formatDateTime, formatVnd, maskAccount } from "../../../../lib/transactions";
import type { FeedbackState, Transaction } from "../../../../lib/types";

type ViewState = "loading" | "ready" | "denied" | "not_found" | "error";

export default function ApprovalDetailPage() {
  const params = useParams<{ reference: string }>();
  const router = useRouter();
  const { user, request } = useAuth();
  const reference = params.reference;
  const [view, setView] = useState<ViewState>("loading");
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setView("loading");
    setFeedback(null);
    try {
      setTransaction(await request<Transaction>(`/approvals/${reference}`));
      setView("ready");
    } catch (failure) {
      const error = failure instanceof ApiError
        ? failure
        : new ApiError(0, "Không thể tải giao dịch");
      if (error.status === 403) setView("denied");
      else if (error.status === 404) setView("not_found");
      else setView("error");
    }
  }, [reference, request]);

  useEffect(() => { load(); }, [load]);

  const backPath = user?.roles.includes("controller") ? "/approvals" : "/transactions";

  const approve = async () => {
    if (!transaction || !window.confirm(`Phê duyệt giao dịch ${transaction.reference}?`)) return;
    setBusy(true);
    try {
      const updated = await request<Transaction>(
        `/transactions/${transaction.reference}/approve`,
        { method: "POST" },
      );
      setTransaction(updated);
      setFeedback({
        kind: "success",
        title: "Phê duyệt thành công",
        message: `${updated.reference} đã chuyển sang trạng thái Đã phê duyệt.`,
      });
    } catch (failure) {
      const error = failure instanceof ApiError
        ? failure
        : new ApiError(0, "Không thể phê duyệt giao dịch");
      setFeedback({
        kind: "error",
        title: error.status === 409 ? "Giao dịch đã được xử lý" : "Không thể phê duyệt",
        message: error.message,
      });
      if (error.status === 409) await load();
    } finally {
      setBusy(false);
    }
  };

  if (view === "loading") {
    return <section className="access-state"><p>Đang tải giao dịch…</p></section>;
  }
  if (view === "denied") {
    return <section className="access-state denied-state">
      <span aria-hidden="true">!</span>
      <p className="kicker">QUYỀN TRUY CẬP</p>
      <h1>Không có quyền truy cập</h1>
      <p>Vai trò hiện tại không được phép phê duyệt giao dịch này.</p>
      <button className="button secondary" onClick={() => router.push("/transactions")}>Quay lại giao dịch</button>
    </section>;
  }
  if (view === "not_found") {
    return <section className="access-state">
      <p className="kicker">TRA CỨU GIAO DỊCH</p>
      <h1>Không tìm thấy giao dịch</h1>
      <p>Mã giao dịch không tồn tại hoặc không còn khả dụng.</p>
      <button className="button secondary" onClick={() => router.push(backPath)}>Quay lại</button>
    </section>;
  }
  if (view === "error" || !transaction) {
    return <section className="access-state">
      <p className="kicker">KẾT NỐI HỆ THỐNG</p>
      <h1>Không thể tải giao dịch</h1>
      <p>Vui lòng thử lại sau ít phút.</p>
      <button className="button secondary" onClick={load}>Thử lại</button>
    </section>;
  }

  return <div className="page-stack">
    <header className="page-header"><div>
      <p className="kicker">HỒ SƠ PHÊ DUYỆT</p>
      <h1>Chi tiết giao dịch</h1>
      <p>Kiểm tra thông tin trước khi đưa ra quyết định.</p>
    </div></header>
    <Feedback value={feedback} onClose={() => setFeedback(null)} />
    <section className="panel approval-detail">
      <div className="transaction-head"><div><small>MÃ GIAO DỊCH</small><b>{transaction.reference}</b></div>
        <span className={`status status-${transaction.status}`}>{transaction.status === "pending" ? "Chờ phê duyệt" : "Đã phê duyệt"}</span>
      </div>
      <div className="transaction-amount">{formatVnd(transaction.amount_vnd)}</div>
      <div className="transaction-detail"><span><small>Từ tài khoản</small>{maskAccount(transaction.source_account)}</span><i>→</i><span><small>Đến {transaction.beneficiary_name}</small>{maskAccount(transaction.destination_account)}</span></div>
      <dl className="approval-facts"><div><dt>Nội dung</dt><dd>{transaction.description}</dd></div><div><dt>Người tạo</dt><dd>{transaction.created_by}</dd></div><div><dt>Thời gian tạo</dt><dd>{formatDateTime(transaction.created_at)}</dd></div>{transaction.approved_by && <div><dt>Người duyệt</dt><dd>{transaction.approved_by}</dd></div>}</dl>
      <div className="approval-actions"><button className="button secondary" onClick={() => router.push(backPath)}>Quay lại</button>{transaction.status === "pending" && <button className="button primary" disabled={busy} onClick={approve}>{busy ? "Đang phê duyệt…" : "Phê duyệt giao dịch"}</button>}</div>
    </section>
  </div>;
}
```

- [ ] **Step 6: Xóa BackendProof và kiểm tra type/build**

Dùng `apply_patch` xóa `web/components/BackendProof.tsx`, rồi chạy:

```bash
cd web
npm test
npm run build
```

Expected: tests pass; build route list có `/approvals/[reference]`; TypeScript
không còn reference tới proof props hoặc `FeedbackState.endpoint/status`.

- [ ] **Step 7: Commit direct approval flow**

```bash
git add web/components/BackendProof.tsx web/components/TransactionList.tsx web/components/Feedback.tsx web/lib/types.ts 'web/app/(portal)/transactions/page.tsx' 'web/app/(portal)/approvals/page.tsx' 'web/app/(portal)/approvals/[reference]/page.tsx'
git commit -m "feat: add protected approval detail journey"
```

---

### Task 4: Làm sạch toàn bộ product copy và route quản trị

**Files:**
- Create: `web/tests/product-copy.test.ts`
- Modify: `web/lib/api.ts`
- Modify: `web/app/login/page.tsx`
- Modify: `web/components/AppShell.tsx`
- Delete: `web/app/(portal)/admin/demo-control/page.tsx`
- Create: `web/app/(portal)/admin/policies/page.tsx`
- Modify: `web/app/(portal)/admin/users/page.tsx`
- Modify: `web/app/(portal)/transactions/page.tsx`
- Modify: `web/app/(portal)/approvals/page.tsx`
- Modify: `web/app/(portal)/audit/page.tsx`
- Modify: `web/lib/access.ts`
- Modify: `web/tests/access.test.ts`

**Interfaces:**
- Consumes: `modePresentation`, `auditOutcomeLabel`, `auditActionLabel`.
- Produces: Rendered copy không còn chuỗi hướng dẫn/API; Admin UI ở `/admin/policies`.

- [ ] **Step 1: Viết static regression test cho forbidden copy**

Tạo `web/tests/product-copy.test.ts`:

```typescript
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const renderedFiles = [
  "app/login/page.tsx",
  "components/AppShell.tsx",
  "components/Feedback.tsx",
  "components/TransactionList.tsx",
  "app/(portal)/transactions/page.tsx",
  "app/(portal)/approvals/page.tsx",
  "app/(portal)/approvals/[reference]/page.tsx",
  "app/(portal)/admin/policies/page.tsx",
  "app/(portal)/admin/users/page.tsx",
  "app/(portal)/audit/page.tsx",
];

const forbidden = [
  "FastAPI ·",
  "127.0.0.1:8000/health",
  "Kiểm tra bảo vệ backend",
  "Gửi thử request vượt quyền",
  "DỮ LIỆU TỪ SQLITE",
  "KỊCH BẢN 5 BƯỚC",
  "Điều khiển demo",
  "Đăng nhập qua backend",
  "PHIÊN ĐĂNG NHẬP THẬT",
  "endpoint được bảo vệ",
  "HTTP 403",
];

describe("product-facing copy", () => {
  it("does not expose technical demo instructions", () => {
    const source = renderedFiles
      .map((file) => readFileSync(resolve(process.cwd(), file), "utf8"))
      .join("\n");
    for (const phrase of forbidden) expect(source).not.toContain(phrase);
  });
});
```

Trong `web/tests/access.test.ts`, đổi expectation Admin thành:

```typescript
expect(navigationFor(["administrator"]).map((item) => item.href)).toEqual([
  "/admin/users",
  "/admin/policies",
  "/audit",
]);
expect(navigationFor(["administrator"])[1].label).toBe("Chính sách phê duyệt");
expect(roleHome(["administrator"])).toBe("/admin/policies");
```

- [ ] **Step 2: Chạy test để xác nhận RED**

Run:

```bash
cd web
npm test -- product-copy.test.ts
```

Expected: FAIL vì login, shell, users, transactions và trang Admin còn forbidden
copy; file policies có thể chưa tồn tại.

- [ ] **Step 3: Làm sạch login và network error**

Trong `web/lib/api.ts`, đổi network message thành:

```typescript
throw new ApiError(0, "Không thể kết nối hệ thống. Vui lòng thử lại hoặc liên hệ quản trị viên.");
```

Trong login page:

- xóa import/export use của `API_BASE`;
- initial username/password là chuỗi rỗng;
- xóa `useDemoAccount`, `server-line`, `demo-accounts`, story steps và mọi health
  hint;
- hero dùng copy:

```tsx
<p className="kicker light">CỔNG NGHIỆP VỤ NỘI BỘ</p>
<h1>Vận hành giao dịch<br /><em>an toàn và nhất quán.</em></h1>
<p className="login-lead">Không gian làm việc dành cho nhân viên Nova Bank.</p>
```

- form intro là “Sử dụng tài khoản nội bộ đã được cấp.”;
- button là “Đăng nhập”.

- [ ] **Step 4: Dùng mode business copy trong AppShell**

Import `modePresentation`, lấy `const policy = modePresentation(mode)` và render:

```tsx
<div className={`mode-banner mode-${mode}`}>
  <div><strong>{policy.title}</strong><span>{policy.description}</span></div>
  <b>{mode === "rbac" ? "ĐANG ÁP DỤNG" : "CHÍNH SÁCH HIỆN TẠI"}</b>
</div>
```

- [ ] **Step 5: Đổi trang Admin sang Chính sách phê duyệt**

Dùng `apply_patch` tạo `web/app/(portal)/admin/policies/page.tsx` từ logic state,
PATCH và reset hiện có. Product copy bắt buộc:

- header: “Chính sách phê duyệt” / “Thiết lập quy trình kiểm soát giao dịch.”;
- baseline card: “Kiểm soát cơ bản” / “Giao dịch viên có thể hoàn tất giao dịch
  trong một bước.”;
- RBAC card: “Phân tách nhiệm vụ” / “Giao dịch cần Kiểm soát viên độc lập phê
  duyệt.”;
- buttons: “Áp dụng kiểm soát cơ bản”, “Áp dụng phân tách nhiệm vụ”;
- feedback: “Đã cập nhật chính sách”;
- reset section: “Khôi phục dữ liệu” và button cùng tên;
- confirm reset: “Khôi phục toàn bộ dữ liệu về trạng thái ban đầu?”;
- không render journey list, API, backend, permission, bypass hoặc chữ demo.

Sau đó dùng `apply_patch` xóa
`web/app/(portal)/admin/demo-control/page.tsx`.

Trong `web/lib/access.ts`, thay navigation item và Admin home:

```typescript
{ href: "/admin/policies", label: "Chính sách phê duyệt", shortLabel: "CS" }
```

```typescript
if (roles.includes("administrator")) return "/admin/policies";
```

- [ ] **Step 6: Làm sạch copy trên users, transactions và approvals**

Thay các phrase:

```text
TẠO TRỰC TIẾP KHI DEMO → THÊM NHÂN VIÊN
DỮ LIỆU TỪ SQLITE → DANH SÁCH HIỆN TẠI
trạng thái đã được backend cập nhật → giao dịch đã được cập nhật
FOUR-EYES CONTROL → PHÂN TÁCH NHIỆM VỤ
```

Xóa mọi status field khỏi FeedbackState. Page header/empty states chỉ mô tả
nghiệp vụ, không giải thích demo hoặc implementation.

- [ ] **Step 7: Dịch audit UI**

Trong audit page import helper và thay:

```tsx
<b>{auditActionLabel(event.resource, event.action)}</b>
```

thay cho raw `{event.resource}:{event.action}`, và:

```tsx
<em className={`outcome outcome-${event.outcome}`}>
  {auditOutcomeLabel(event.outcome)}
</em>
```

Select filter giữ raw value làm query nhưng label hiển thị tiếng Việt. Header
copy là “Lịch sử hoạt động” / “Theo dõi các thay đổi và quyết định truy cập
trong hệ thống.”; không nhắc SQLite hoặc backend. Xóa render
`{event.detail}` vì đây là raw audit detail dành cho kỹ thuật. Hiển thị role qua
`roleLabels[event.role_at_event] ?? "Hệ thống"` thay vì raw `administrator`,
`teller` hoặc `controller`.

- [ ] **Step 8: Chạy copy test, unit tests, build và commit**

Run:

```bash
cd web
npm test
npm run build
```

Expected: all tests pass; build có `/admin/policies` và không có
`/admin/demo-control`.

Commit:

```bash
git add web/tests/product-copy.test.ts web/lib/api.ts web/lib/access.ts web/tests/access.test.ts web/app/login/page.tsx web/components/AppShell.tsx 'web/app/(portal)/admin/demo-control/page.tsx' 'web/app/(portal)/admin/policies/page.tsx' 'web/app/(portal)/admin/users/page.tsx' 'web/app/(portal)/transactions/page.tsx' 'web/app/(portal)/approvals/page.tsx' 'web/app/(portal)/audit/page.tsx'
git commit -m "refactor: present RBAC portal as a banking product"
```

---

### Task 5: Áp dụng typography dễ đọc trên toàn portal

**Files:**
- Create: `web/tests/typography.test.ts`
- Modify: `web/app/globals.css`

**Interfaces:**
- Consumes: Class names hiện có và các class mới `waiting-approval`, `access-state`, `approval-detail`.
- Produces: Một visual system sans-serif, body 16px, không có font-size dưới 14px hoặc hidden labels bằng font-size 0.

- [ ] **Step 1: Viết failing typography regression test**

Tạo `web/tests/typography.test.ts`:

```typescript
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "app/globals.css"), "utf8");

describe("portal typography", () => {
  it("uses one accessible sans-serif stack", () => {
    expect(css).toContain('Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif');
    expect(css).not.toMatch(/Georgia|Times New Roman/);
    expect(css).not.toMatch(/font-size:\s*0(?:px)?\s*;/);
  });

  it("never sets pixel font sizes below 14px", () => {
    const sizes = [...css.matchAll(/font-size:\s*(\d+(?:\.\d+)?)px/g)].map(
      (match) => Number(match[1]),
    );
    expect(sizes.length).toBeGreaterThan(0);
    expect(sizes.filter((size) => size < 14)).toEqual([]);
  });

  it("sets the body copy to 16px", () => {
    expect(css).toMatch(/body\s*\{[^}]*font-size:\s*16px/s);
  });
});
```

- [ ] **Step 2: Chạy test để xác nhận RED**

Run:

```bash
cd web
npm test -- typography.test.ts
```

Expected: FAIL với Georgia/Times, font-size 0 và nhiều size 8–11px.

- [ ] **Step 3: Đặt typography foundation**

Trong `globals.css`, body phải có:

```css
body {
  margin: 0;
  background: var(--canvas);
  color: var(--ink);
  font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
}
```

Xóa tất cả font shorthand dùng Georgia. Dùng:

```css
.login-story h1 { font-size: clamp(48px, 5vw, 64px); line-height: 1.05; }
.login-card h2 { font-size: 34px; line-height: 1.2; }
.page-header h1 { font-size: clamp(34px, 4vw, 40px); line-height: 1.15; }
.section-heading h2,
.form-section-title b { font-size: 21px; }
.transaction-amount { font-size: 30px; }
```

- [ ] **Step 4: Nâng toàn bộ supporting text lên tối thiểu 14px**

Áp dụng bảng:

| Selector group | Font size |
| --- | --- |
| `.kicker`, header small, card small, badge, outcome | 14px |
| form labels, `.button`, feedback, transaction detail/meta | 14px |
| nav, actor name, logout, policy banner | 15px |
| regular paragraphs, login lead | 16px |

Tăng button padding tối thiểu `13px 16px`, input padding `13px 14px`, panel
padding `26px`, transaction card padding `22px`, sidebar width khoảng `260px`.
Thêm:

```css
.waiting-approval {
  padding: 14px 16px;
  border: 1px solid #b9cbe4;
  border-radius: 9px;
  background: #eef4fc;
  color: #294d7c;
  font-size: 14px;
  font-weight: 700;
}

.access-state {
  max-width: 680px;
  margin: 64px auto;
  padding: 44px;
  text-align: center;
  background: white;
  border: 1px solid var(--line);
  border-radius: 16px;
}

.access-state h1 { margin: 12px 0; font-size: 38px; }
.access-state > span { display: inline-grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; font-size: 28px; }
```

- [ ] **Step 5: Sửa responsive mà không ẩn label**

Trong media queries:

- xóa mọi `font-size: 0` ở brand/nav;
- mobile nav dùng `display:flex; overflow-x:auto;` và giữ text 14px;
- audit row `min-width` đủ cho text 14px và table cuộn ngang;
- page title mobile không nhỏ hơn 32px;
- form/policy/card chuyển một cột dưới 620px.

- [ ] **Step 6: Chạy typography test, toàn bộ test và build**

Run:

```bash
cd web
npm test
npm run build
```

Expected: typography tests pass; toàn bộ Vitest pass; Next.js build thành công.

- [ ] **Step 7: Commit typography**

```bash
git add web/tests/typography.test.ts web/app/globals.css
git commit -m "style: improve portal typography and readability"
```

---

### Task 6: Cập nhật kịch bản và xác minh end-to-end

**Files:**
- Modify: `DEMO_RBAC_NOVA_BANK.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: UI terminology and direct approval route from Tasks 1–5.
- Produces: Demo guide matching the implemented product flow.

- [ ] **Step 1: Cập nhật thuật ngữ trong tài liệu duy nhất**

Trong `DEMO_RBAC_NOVA_BANK.md`, thay:

```text
Điều khiển demo → Chính sách phê duyệt
BASELINE → Kiểm soát cơ bản
SECURE MODE → Phân tách nhiệm vụ
Đặt lại toàn bộ dữ liệu demo → Khôi phục dữ liệu
Tự phê duyệt giao dịch → Hoàn tất giao dịch
```

Không đổi endpoint/health commands trong phần cài đặt vì đó là tài liệu kỹ
thuật, không phải product surface.

- [ ] **Step 2: Thay checkpoint proof bằng direct URL journey**

Phần Teller sau RBAC phải hướng dẫn:

1. Tạo giao dịch thứ hai và sao chép/ghi lại reference.
2. Trong cùng tab Teller, mở
   `http://localhost:3000/approvals/<reference>`.
3. Quan sát “Không có quyền truy cập”.
4. Quay lại giao dịch và xác nhận vẫn “Chờ phê duyệt”.
5. Controller mở hàng đợi, chọn “Xem và phê duyệt”, rồi approve.
6. Admin mở audit và thấy “Đã từ chối”, “Đã cho phép”, “Thành công”.

Xóa mọi hướng dẫn bấm panel proof hoặc quan sát raw endpoint/permission trên UI.

- [ ] **Step 3: Rà README không mô tả UI cũ**

README chỉ giữ link tới `DEMO_RBAC_NOVA_BANK.md`. Nếu đoạn giới thiệu Nova Bank
còn nhắc panel “Kiểm tra bảo vệ backend”, thay bằng “Teller truy cập trực tiếp
trang phê duyệt và bị từ chối; Controller phê duyệt thành công.”

- [ ] **Step 4: Chạy các phép rà source và tài liệu**

Run:

```bash
set -e
! rg -n 'Kiểm tra bảo vệ backend|Gửi thử request vượt quyền|DỮ LIỆU TỪ SQLITE|KỊCH BẢN 5 BƯỚC|Điều khiển demo|Đăng nhập qua backend|PHIÊN ĐĂNG NHẬP THẬT|FastAPI ·|HTTP 403' web/app web/components
! rg -n -P 'Georgia|Times New Roman|font-size:\s*(?:0|[1-9]|1[0-3])px\s*;' web/app/globals.css
! rg -n 'Kiểm tra bảo vệ backend|Gửi thử request vượt quyền|transactions:approve' README.md DEMO_RBAC_NOVA_BANK.md
rg -n 'Không có quyền truy cập|Chính sách phê duyệt|Phân tách nhiệm vụ' DEMO_RBAC_NOVA_BANK.md
git diff --check
```

Expected: ba negative searches không có output; guide có ba checkpoint mới;
không có whitespace error.

- [ ] **Step 5: Chạy toàn bộ verification**

Run backend:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest -q
```

Run frontend:

```bash
cd web
npm test
npm run build
```

Expected: toàn bộ pytest/Vitest pass và production build thành công.

- [ ] **Step 6: Smoke-test health và full RBAC API journey**

Chạy từ repo root:

```bash
set -e
SMOKE_DIR=$(mktemp -d)
RBAC_DEMO_DB="$SMOKE_DIR/rbac.db" UV_CACHE_DIR=.uv-cache uv run uvicorn rbac_guard.api:app --host 127.0.0.1 --port 8100 >"$SMOKE_DIR/api.log" 2>&1 &
API_PID=$!
cleanup() {
  kill "$API_PID" 2>/dev/null || true
  wait "$API_PID" 2>/dev/null || true
  rm -rf "$SMOKE_DIR"
}
trap cleanup EXIT
for attempt in 1 2 3 4 5; do
  curl -fsS http://127.0.0.1:8100/health && break
  sleep 1
done
BASE_URL=http://127.0.0.1:8100 uv run python - <<'PY'
import os
import httpx

base = os.environ["BASE_URL"]
client = httpx.Client(base_url=base, timeout=5)

def login(username: str, password: str) -> str:
    response = client.post("/auth/login", json={"username": username, "password": password})
    response.raise_for_status()
    return response.json()["token"]

def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

admin = login("admin01", "Admin@123")
created_user = client.post(
    "/users",
    headers=headers(admin),
    json={
        "username": "lan.demo",
        "display_name": "Lan Nguyễn",
        "password": "Lan@1234",
        "role": "teller",
    },
)
created_user.raise_for_status()
teller = login("lan.demo", "Lan@1234")
created_transaction = client.post(
    "/transactions",
    headers=headers(teller),
    json={
        "source_account": "001100001234",
        "destination_account": "002200005678",
        "beneficiary_name": "Lê Bình",
        "amount_vnd": 50_000_000,
        "description": "Thanh toán hợp đồng",
    },
)
created_transaction.raise_for_status()
reference = created_transaction.json()["reference"]
mode = client.patch(
    "/demo/security-mode",
    headers=headers(admin),
    json={"mode": "rbac"},
)
mode.raise_for_status()

teller_approval_view = client.get(f"/approvals/{reference}", headers=headers(teller))
assert teller_approval_view.status_code == 403, teller_approval_view.text

controller = login("controller01", "Controller@123")
controller_approval_view = client.get(f"/approvals/{reference}", headers=headers(controller))
assert controller_approval_view.status_code == 200, controller_approval_view.text
approved = client.post(f"/transactions/{reference}/approve", headers=headers(controller))
approved.raise_for_status()
assert approved.json()["approved_by"] == "controller01"

audit = client.get("/audit-logs", headers=headers(admin)).json()
assert any(
    event["action"] == "review"
    and event["outcome"] == "denied"
    and event["transaction_reference"] == reference
    for event in audit
)
print({"reference": reference, "teller": 403, "controller": "approved", "audit": "denied recorded"})
PY
```

Expected: health `status=ok` và tất cả assertions pass; dừng đúng PID server.

- [ ] **Step 7: Commit docs and final state**

```bash
git add DEMO_RBAC_NOVA_BANK.md README.md
git commit -m "docs: update product-like RBAC demo journey"
git status --short --branch
```

Expected: branch clean; `Khung_dan_y_v3.md` vẫn chỉ tồn tại untracked tại
checkout gốc, không nằm trong commit.
