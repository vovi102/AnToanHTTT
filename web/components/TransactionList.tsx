"use client";

import Link from "next/link";

import { approvalPresentation, formatDateTime, formatVnd, maskAccount } from "../lib/transactions";
import type { SecurityMode, Transaction } from "../lib/types";

type TransactionListProps = {
  transactions: Transaction[];
  mode: SecurityMode;
  roles: string[];
  busyReference?: string | null;
  onApprove?: (transaction: Transaction) => void;
};

export function TransactionList({ transactions, mode, roles, busyReference, onApprove }: TransactionListProps) {
  const presentation = approvalPresentation(mode, roles);
  if (!transactions.length) return <div className="empty-state"><b>Chưa phát sinh giao dịch</b></div>;
  return <div className="transaction-stack">{transactions.map((transaction) => (
    <article className="transaction-card" key={transaction.reference}>
      <div className="transaction-head"><div><small>MÃ GIAO DỊCH</small><b>{transaction.reference}</b></div><span className={`status status-${transaction.status}`}>{transaction.status === "pending" ? "Chờ phê duyệt" : "Đã phê duyệt"}</span></div>
      <div className="transaction-amount">{formatVnd(transaction.amount_vnd)}</div>
      <div className="transaction-detail"><span><small>Từ tài khoản</small>{maskAccount(transaction.source_account)}</span><i>→</i><span><small>Đến {transaction.beneficiary_name}</small>{maskAccount(transaction.destination_account)}</span></div>
      <div className="transaction-meta"><span>Tạo bởi <b>{transaction.created_by}</b> · {formatDateTime(transaction.created_at)}</span>{transaction.approved_by && <span>Duyệt bởi <b>{transaction.approved_by}</b> · {formatDateTime(transaction.approved_at)}</span>}</div>
      {transaction.status === "pending" && presentation === "self_approve" && <div className="baseline-action"><p>Giao dịch có thể được hoàn tất theo chính sách hiện tại.</p><button className="button warning" disabled={busyReference === transaction.reference} onClick={() => onApprove?.(transaction)}>{busyReference === transaction.reference ? "Đang xử lý…" : "Hoàn tất giao dịch"}</button></div>}
      {transaction.status === "pending" && presentation === "approval_link" && <Link className="button primary" href={`/approvals/${transaction.reference}`}>Xem và phê duyệt <span>→</span></Link>}
      {transaction.status === "pending" && presentation === "waiting" && <div className="waiting-approval">Đang chờ Kiểm soát viên phê duyệt</div>}
    </article>
  ))}</div>;
}
