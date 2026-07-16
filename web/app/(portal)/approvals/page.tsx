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
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const refresh = useCallback(async () => {
    try { setTransactions(await request<Transaction[]>("/transactions")); }
    catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải hàng đợi"); setFeedback({ kind: "error", title: "Không thể tải hàng đợi", message: error.message }); }
  }, [request]);
  useEffect(() => { refresh(); window.addEventListener("focus", refresh); return () => window.removeEventListener("focus", refresh); }, [refresh]);

  const pending = transactions.filter((item) => item.status === "pending");
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">KIỂM SOÁT GIAO DỊCH</p><h1>Hàng đợi phê duyệt</h1><p>Kiểm tra giao dịch được tạo tại quầy trước khi phê duyệt.</p></div><div className="header-stat accent"><small>CHỜ XỬ LÝ</small><b>{pending.length}</b></div></header><Feedback value={feedback} onClose={() => setFeedback(null)} /><section className="panel"><div className="section-heading"><div><p className="kicker">FOUR-EYES CONTROL</p><h2>Giao dịch đang chờ</h2></div><button className="button secondary" onClick={refresh}>Tải lại</button></div><TransactionList transactions={pending} mode="rbac" roles={user?.roles ?? []} /></section></div>;
}
