import { describe, expect, it } from "vitest";

import { approvalPresentation, formatVnd } from "../lib/transactions";

describe("transaction presentation", () => {
  it("shows self approval only to tellers in baseline mode", () => {
    expect(approvalPresentation("baseline", ["teller"])).toBe("self_approve");
    expect(approvalPresentation("rbac", ["teller"])).toBe("backend_proof");
  });

  it("shows normal approval only to controllers", () => {
    expect(approvalPresentation("rbac", ["controller"])).toBe("approve");
    expect(approvalPresentation("rbac", ["auditor"])).toBe("none");
    expect(approvalPresentation("rbac", ["administrator"])).toBe("none");
  });

  it("formats integer VND amounts for the Vietnamese demo", () => {
    expect(formatVnd(50_000_000)).toContain("50.000.000");
  });
});
