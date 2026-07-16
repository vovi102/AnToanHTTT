import type { SecurityMode } from "./types";

export type ApprovalPresentation = "self_approve" | "backend_proof" | "approve" | "none";

export function approvalPresentation(mode: SecurityMode, roles: string[]): ApprovalPresentation {
  if (roles.includes("controller")) return "approve";
  if (!roles.includes("teller")) return "none";
  return mode === "baseline" ? "self_approve" : "backend_proof";
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
