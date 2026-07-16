"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useAuth } from "../../../../components/AuthProvider";
import { Feedback } from "../../../../components/Feedback";
import { ApiError } from "../../../../lib/api";
import { formatDateTime, formatVnd, maskAccount } from "../../../../lib/transactions";
import type { FeedbackState, Transaction } from "../../../../lib/types";

type ViewState = "loading" | "ready" | "denied" | "not_found" | "error";

export default function ApprovalDetailPage() {
  const params = useParams<{ reference: string }>();
  const router = useRouter();
  const { user, request } = useAuth();
  const reference = params.reference;
  const [view, setView] = useState<ViewState>("loading");
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setView("loading");
    setFeedback(null);
    try {
      setTransaction(await request<Transaction>(`/approvals/${reference}`));
      setView("ready");
    } catch (failure) {
      const error = failure instanceof ApiError
        ? failure
        : new ApiError(0, "Không thể tải giao dịch");
      if (error.status === 403) setView("denied");
      else if (error.status === 404) setView("not_found");
      else setView("error");
    }
  }, [reference, request]);

  useEffect(() => { load(); }, [load]);

  const backPath = user?.roles.includes("controller") ? "/approvals" : "/transactions";

  const approve = async () => {
    if (!transaction || !window.confirm(`Phê duyệt giao dịch ${transaction.reference}?`)) return;
    setBusy(true);
    try {
      const updated = await request<Transaction>(
        `/transactions/${transaction.reference}/approve`,
        { method: "POST" },
      );
      setTransaction(updated);
      setFeedback({
        kind: "success",
        title: "Phê duyệt thành công",
        message: `${updated.reference} đã chuyển sang trạng thái Đã phê duyệt.`,
      });
    } catch (failure) {
      const error = failure instanceof ApiError
        ? failure
        : new ApiError(0, "Không thể phê duyệt giao dịch");
      setFeedback({
        kind: "error",
        title: error.status === 409 ? "Giao dịch đã được xử lý" : "Không thể phê duyệt",
        message: error.message,
      });
      if (error.status === 409) await load();
    } finally {
      setBusy(false);
    }
  };

  if (view === "loading") {
    return <section className="access-state"><p>Đang tải giao dịch…</p></section>;
  }
  if (view === "denied") {
    return <section className="access-state denied-state">
      <span aria-hidden="true">!</span>
      <p className="kicker">QUYỀN TRUY CẬP</p>
      <h1>Không có quyền truy cập</h1>
      <p>Vai trò hiện tại không được phép phê duyệt giao dịch này.</p>
      <button className="button secondary" onClick={() => router.push("/transactions")}>Quay lại giao dịch</button>
    </section>;
  }
  if (view === "not_found") {
    return <section className="access-state">
      <p className="kicker">TRA CỨU GIAO DỊCH</p>
      <h1>Không tìm thấy giao dịch</h1>
      <p>Mã giao dịch không tồn tại hoặc không còn khả dụng.</p>
      <button className="button secondary" onClick={() => router.push(backPath)}>Quay lại</button>
    </section>;
  }
  if (view === "error" || !transaction) {
    return <section className="access-state">
      <p className="kicker">KẾT NỐI HỆ THỐNG</p>
      <h1>Không thể tải giao dịch</h1>
      <p>Vui lòng thử lại sau ít phút.</p>
      <button className="button secondary" onClick={load}>Thử lại</button>
    </section>;
  }

  return <div className="page-stack">
    <header className="page-header"><div>
      <p className="kicker">HỒ SƠ PHÊ DUYỆT</p>
      <h1>Chi tiết giao dịch</h1>
      <p>Kiểm tra thông tin trước khi đưa ra quyết định.</p>
    </div></header>
    <Feedback value={feedback} onClose={() => setFeedback(null)} />
    <section className="panel approval-detail">
      <div className="transaction-head"><div><small>MÃ GIAO DỊCH</small><b>{transaction.reference}</b></div>
        <span className={`status status-${transaction.status}`}>{transaction.status === "pending" ? "Chờ phê duyệt" : "Đã phê duyệt"}</span>
      </div>
      <div className="transaction-amount">{formatVnd(transaction.amount_vnd)}</div>
      <div className="transaction-detail"><span><small>Từ tài khoản</small>{maskAccount(transaction.source_account)}</span><i>→</i><span><small>Đến {transaction.beneficiary_name}</small>{maskAccount(transaction.destination_account)}</span></div>
      <dl className="approval-facts"><div><dt>Nội dung</dt><dd>{transaction.description}</dd></div><div><dt>Người tạo</dt><dd>{transaction.created_by}</dd></div><div><dt>Thời gian tạo</dt><dd>{formatDateTime(transaction.created_at)}</dd></div>{transaction.approved_by && <div><dt>Người duyệt</dt><dd>{transaction.approved_by}</dd></div>}</dl>
      <div className="approval-actions"><button className="button secondary" onClick={() => router.push(backPath)}>Quay lại</button>{transaction.status === "pending" && <button className="button primary" disabled={busy} onClick={approve}>{busy ? "Đang phê duyệt…" : "Phê duyệt giao dịch"}</button>}</div>
    </section>
  </div>;
}
