import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const renderedFiles = [
  "app/layout.tsx",
  "app/login/page.tsx",
  "components/AppShell.tsx",
  "components/Feedback.tsx",
  "components/TransactionForm.tsx",
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
  "Demo nghiệp vụ ngân hàng",
  "endpoint được bảo vệ",
  "HTTP 403",
  "SQLite",
];

describe("product-facing copy", () => {
  it("does not expose technical demo instructions", () => {
    const source = renderedFiles
      .map((file) => readFileSync(resolve(process.cwd(), file), "utf8"))
      .join("\n")
      .toLowerCase();
    for (const phrase of forbidden) expect(source).not.toContain(phrase.toLowerCase());
  });
});
