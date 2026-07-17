import type { SecurityMode } from "./types";

export type ApprovalPresentation =
  | "self_approve"
  | "approval_link"
  | "waiting"
  | "none";

export function approvalPresentation(mode: SecurityMode, roles: string[]): ApprovalPresentation {
  if (roles.includes("controller")) return "approval_link";
  if (!roles.includes("teller")) return "none";
  return mode === "baseline" ? "self_approve" : "waiting";
}

export function formatVnd(value: number): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatDateTime(value: string | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function maskAccount(value: string): string {
  return value.length <= 4 ? value : `•••• ${value.slice(-4)}`;
}
