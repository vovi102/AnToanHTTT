"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "../../../components/AuthProvider";
import { Feedback } from "../../../components/Feedback";
import { TransactionList } from "../../../components/TransactionList";
import { ApiError } from "../../../lib/api";
import type { FeedbackState, Transaction } from "../../../lib/types";

export default function ApprovalsPage() {
  const { user, request } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const refresh = useCallback(async () => {
    try { setTransactions(await request<Transaction[]>("/transactions")); }
    catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải hàng đợi"); setFeedback({ kind: "error", title: "Không thể tải hàng đợi", message: error.message, status: error.status }); }
  }, [request]);
  useEffect(() => { refresh(); window.addEventListener("focus", refresh); return () => window.removeEventListener("focus", refresh); }, [refresh]);

  const approve = async (transaction: Transaction) => {
    if (!window.confirm(`Kiểm soát viên xác nhận phê duyệt ${transaction.reference}?`)) return;
    setBusy(transaction.reference);
    try {
      const updated = await request<Transaction>(`/transactions/${transaction.reference}/approve`, { method: "POST" });
      setTransactions((rows) => rows.map((item) => item.reference === updated.reference ? updated : item));
      setFeedback({ kind: "success", title: "Phê duyệt thành công", message: `${updated.reference} đã chuyển sang trạng thái Đã phê duyệt.` });
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể phê duyệt");
      setFeedback({ kind: "error", title: error.status === 409 ? "Giao dịch đã được xử lý" : "Không thể phê duyệt", message: error.message, status: error.status });
      if (error.status === 409) await refresh();
    } finally { setBusy(null); }
  };
  const pending = transactions.filter((item) => item.status === "pending");
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">KIỂM SOÁT GIAO DỊCH</p><h1>Hàng đợi phê duyệt</h1><p>Kiểm tra giao dịch được tạo tại quầy trước khi phê duyệt.</p></div><div className="header-stat accent"><small>CHỜ XỬ LÝ</small><b>{pending.length}</b></div></header><Feedback value={feedback} onClose={() => setFeedback(null)} /><section className="panel"><div className="section-heading"><div><p className="kicker">FOUR-EYES CONTROL</p><h2>Giao dịch đang chờ</h2></div><button className="button secondary" onClick={refresh}>Tải lại</button></div><TransactionList transactions={pending} mode="rbac" roles={user?.roles ?? []} busyReference={busy} proof={{}} onApprove={approve} onProof={() => undefined} /></section></div>;
}
