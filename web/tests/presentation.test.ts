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
