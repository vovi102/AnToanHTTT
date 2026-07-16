"use client";

import { useCallback, useEffect, useState } from "react";

import { TransactionForm } from "../../../components/TransactionForm";
import { TransactionList } from "../../../components/TransactionList";
import { Feedback } from "../../../components/Feedback";
import { useAuth } from "../../../components/AuthProvider";
import { ApiError } from "../../../lib/api";
import type { FeedbackState, SecurityMode, Transaction } from "../../../lib/types";

export default function TransactionsPage() {
  const { user, request } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [mode, setMode] = useState<SecurityMode>("baseline");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const [proof, setProof] = useState<Record<string, FeedbackState | null>>({});

  const refresh = useCallback(async () => {
    try {
      const [rows, settings] = await Promise.all([
        request<Transaction[]>("/transactions"),
        request<{ mode: SecurityMode }>("/demo/security-mode"),
      ]);
      setTransactions(rows); setMode(settings.mode);
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải giao dịch");
      setFeedback({ kind: "error", title: "Không thể tải dữ liệu", message: error.message, status: error.status });
    } finally { setLoading(false); }
  }, [request]);

  useEffect(() => { refresh(); window.addEventListener("focus", refresh); return () => window.removeEventListener("focus", refresh); }, [refresh]);

  const approve = async (transaction: Transaction) => {
    if (!window.confirm(`Xác nhận phê duyệt ${transaction.reference} trị giá ${transaction.amount_vnd.toLocaleString("vi-VN")} VND?`)) return;
    setBusy(transaction.reference);
    try {
      const updated = await request<Transaction>(`/transactions/${transaction.reference}/approve`, { method: "POST" });
      setTransactions((rows) => rows.map((item) => item.reference === updated.reference ? updated : item));
      setFeedback({ kind: mode === "baseline" ? "error" : "success", title: mode === "baseline" ? "Giao dịch viên đã tự duyệt" : "Đã phê duyệt", message: mode === "baseline" ? "Một người vừa tạo vừa phê duyệt giao dịch. Đây là rủi ro khi chưa áp dụng RBAC." : "Trạng thái đã được backend cập nhật." });
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể phê duyệt");
      setFeedback({ kind: "error", title: "Không thể phê duyệt", message: error.message, status: error.status });
    } finally { setBusy(null); }
  };

  const runProof = async (transaction: Transaction) => {
    setBusy(transaction.reference);
    try {
      await request(`/transactions/${transaction.reference}/approve`, { method: "POST" });
      setProof((values) => ({ ...values, [transaction.reference]: { kind: "error", title: "Request không bị chặn", message: "Hãy kiểm tra security mode ở Admin.", endpoint: `POST /transactions/${transaction.reference}/approve`, status: 200 } }));
      await refresh();
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể kết nối backend");
      const state: FeedbackState = { kind: "proof", title: error.status === 403 ? "Backend đã chặn đúng" : "Không thể hoàn tất kiểm tra", message: error.status === 403 ? "Giao dịch vẫn ở trạng thái Chờ phê duyệt; việc ẩn nút không phải lớp bảo vệ duy nhất." : error.message, endpoint: `POST /transactions/${transaction.reference}/approve`, status: error.status, permission: error.permission };
      setProof((values) => ({ ...values, [transaction.reference]: state }));
      if (error.status === 403) await refresh();
    } finally { setBusy(null); }
  };

  const teller = user?.roles.includes("teller");
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">TRUNG TÂM GIAO DỊCH</p><h1>{teller ? "Giao dịch của tôi" : "Tra cứu giao dịch"}</h1><p>{teller ? "Tạo và theo dõi yêu cầu chuyển khoản tại quầy." : "Theo dõi trạng thái giao dịch phục vụ kiểm toán."}</p></div><div className="header-stat"><small>TỔNG GIAO DỊCH</small><b>{transactions.length}</b></div></header>
    <Feedback value={feedback} onClose={() => setFeedback(null)} />
    {teller && <section className="panel"><TransactionForm onCreated={(created) => { setTransactions((rows) => [created, ...rows]); setFeedback({ kind: "success", title: "Đã tạo yêu cầu", message: `${created.reference} đang chờ phê duyệt tại backend.` }); }} /></section>}
    <section className="panel"><div className="section-heading"><div><p className="kicker">DỮ LIỆU TỪ SQLITE</p><h2>{teller ? "Yêu cầu gần đây" : "Danh sách giao dịch"}</h2></div><button className="button secondary" onClick={refresh}>Tải lại</button></div>{loading ? <div className="empty-state">Đang tải giao dịch…</div> : <TransactionList transactions={transactions} mode={mode} roles={user?.roles ?? []} busyReference={busy} proof={proof} onApprove={approve} onProof={runProof} />}</section>
  </div>;
}
