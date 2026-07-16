import { describe, expect, it } from "vitest";

import { navigationFor, roleHome } from "../lib/access";

describe("role-aware portal navigation", () => {
  it("shows only transaction work to tellers", () => {
    expect(navigationFor(["teller"]).map((item) => item.href)).toEqual([
      "/transactions",
    ]);
    expect(roleHome(["teller"])).toBe("/transactions");
  });

  it("sends controllers to the approval queue", () => {
    expect(navigationFor(["controller"]).map((item) => item.href)).toEqual([
      "/approvals",
    ]);
    expect(roleHome(["controller"])).toBe("/approvals");
  });

  it("shows administration and audit work to administrators", () => {
    expect(navigationFor(["administrator"]).map((item) => item.href)).toEqual([
      "/admin/users",
      "/admin/demo-control",
      "/audit",
    ]);
    expect(roleHome(["administrator"])).toBe("/admin/demo-control");
  });

  it("shows only transaction review and audit to auditors", () => {
    expect(navigationFor(["auditor"]).map((item) => item.href)).toEqual([
      "/transactions",
      "/audit",
    ]);
  });
});
