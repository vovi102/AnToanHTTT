export type Role = "administrator" | "teller" | "controller" | "auditor";

export type User = {
  id: string;
  username: string;
  display_name: string;
  roles: Role[];
};

export type SecurityMode = "baseline" | "rbac";

export type Transaction = {
  id: number;
  reference: string;
  source_account: string;
  destination_account: string;
  beneficiary_name: string;
  amount_vnd: number;
  description: string;
  status: "pending" | "approved";
  created_by: string;
  created_at: string;
  approved_by: string | null;
  approved_at: string | null;
};

export type AuditEvent = {
  id: number;
  created_at: string;
  username: string | null;
  role_at_event: string | null;
  resource: string;
  action: string;
  outcome: "allowed" | "denied" | "success" | "failed" | "baseline_bypass" | "conflict";
  transaction_reference: string | null;
  detail: string;
};

export type ManagedUser = {
  username: string;
  display_name: string;
  status: string;
  roles: Role[];
};

export type FeedbackState = {
  kind: "success" | "error";
  title: string;
  message: string;
};
