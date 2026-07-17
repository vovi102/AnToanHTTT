import type { Role } from "./types";

export type NavigationItem = {
  href: string;
  label: string;
  shortLabel: string;
};

const roleNavigation: Record<Role, NavigationItem[]> = {
  teller: [
    { href: "/transactions", label: "Giao dịch", shortLabel: "GD" },
  ],
  controller: [
    { href: "/approvals", label: "Phê duyệt", shortLabel: "PD" },
  ],
  administrator: [
    { href: "/admin/users", label: "Nhân viên", shortLabel: "NV" },
    { href: "/admin/policies", label: "Chính sách phê duyệt", shortLabel: "CS" },
    { href: "/audit", label: "Nhật ký kiểm toán", shortLabel: "KT" },
  ],
  auditor: [
    { href: "/transactions", label: "Giao dịch", shortLabel: "GD" },
    { href: "/audit", label: "Nhật ký kiểm toán", shortLabel: "KT" },
  ],
};

export function navigationFor(roles: string[]): NavigationItem[] {
  const seen = new Set<string>();
  return roles.flatMap((role) => roleNavigation[role as Role] ?? []).filter((item) => {
    if (seen.has(item.href)) return false;
    seen.add(item.href);
    return true;
  });
}

export function roleHome(roles: string[]): string {
  if (roles.includes("administrator")) return "/admin/policies";
  return navigationFor(roles)[0]?.href ?? "/login";
}

export const roleLabels: Record<string, string> = {
  administrator: "Quản trị viên",
  teller: "Giao dịch viên",
  controller: "Kiểm soát viên",
  auditor: "Kiểm toán viên",
};
