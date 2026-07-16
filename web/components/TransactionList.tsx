"use client";

import { approvalPresentation, formatDateTime, formatVnd, maskAccount } from "../lib/transactions";
import type { FeedbackState, SecurityMode, Transaction } from "../lib/types";
import { BackendProof } from "./BackendProof";

export function TransactionList({ transactions, mode, roles, busyReference, proof, onApprove, onProof }: {
  transactions: Transaction[];
  mode: SecurityMode;
  roles: string[];
  busyReference: string | null;
  proof: Record<string, FeedbackState | null>;
  onApprove: (transaction: Transaction) => void;
  onProof: (transaction: Transaction) => void;
}) {
  const presentation = approvalPresentation(mode, roles);
  if (!transactions.length) return <div className="empty-state"><b>Chưa có giao dịch</b><p>Tạo yêu cầu đầu tiên để bắt đầu kịch bản.</p></div>;
  return <div className="transaction-stack">{transactions.map((transaction) => (
    <article className="transaction-card" key={transaction.reference}>
      <div className="transaction-head"><div><small>MÃ GIAO DỊCH</small><b>{transaction.reference}</b></div><span className={`status status-${transaction.status}`}>{transaction.status === "pending" ? "Chờ phê duyệt" : "Đã phê duyệt"}</span></div>
      <div className="transaction-amount">{formatVnd(transaction.amount_vnd)}</div>
      <div className="transaction-detail"><span><small>Từ tài khoản</small>{maskAccount(transaction.source_account)}</span><i>→</i><span><small>Đến {transaction.beneficiary_name}</small>{maskAccount(transaction.destination_account)}</span></div>
      <div className="transaction-meta"><span>Tạo bởi <b>{transaction.created_by}</b> · {formatDateTime(transaction.created_at)}</span>{transaction.approved_by && <span>Duyệt bởi <b>{transaction.approved_by}</b> · {formatDateTime(transaction.approved_at)}</span>}</div>
      {transaction.status === "pending" && presentation === "self_approve" && <div className="baseline-action"><p><b>Baseline:</b> hệ thống chưa tách quyền tạo và duyệt.</p><button className="button warning" disabled={busyReference === transaction.reference} onClick={() => onApprove(transaction)}>{busyReference === transaction.reference ? "Đang xử lý…" : "Tự phê duyệt giao dịch"}</button></div>}
      {transaction.status === "pending" && presentation === "approve" && <button className="button primary" disabled={busyReference === transaction.reference} onClick={() => onApprove(transaction)}>{busyReference === transaction.reference ? "Đang phê duyệt…" : "Phê duyệt giao dịch"}<span>→</span></button>}
      {transaction.status === "pending" && presentation === "backend_proof" && <BackendProof transaction={transaction} running={busyReference === transaction.reference} result={proof[transaction.reference] ?? null} onRun={() => onProof(transaction)} />}
    </article>
  ))}</div>;
}
