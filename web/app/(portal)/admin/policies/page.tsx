"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "../../../../components/AuthProvider";
import { Feedback } from "../../../../components/Feedback";
import { ApiError } from "../../../../lib/api";
import { modePresentation } from "../../../../lib/presentation";
import type { FeedbackState, SecurityMode } from "../../../../lib/types";

export default function PoliciesPage() {
  const { request, logout } = useAuth();
  const [mode, setMode] = useState<SecurityMode>("baseline");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);

  const refresh = useCallback(async () => {
    try {
      setMode((await request<{ mode: SecurityMode }>("/demo/security-mode")).mode);
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải chính sách");
      setFeedback({ kind: "error", title: "Không thể tải chính sách", message: error.message });
    }
  }, [request]);

  useEffect(() => { refresh(); }, [refresh]);

  const changeMode = async (next: SecurityMode) => {
    const nextPolicy = modePresentation(next);
    if (next === mode || !window.confirm(`Áp dụng chính sách “${nextPolicy.title}”?`)) return;
    setBusy(true);
    try {
      await request("/demo/security-mode", { method: "PATCH", body: JSON.stringify({ mode: next }) });
      setMode(next);
      window.dispatchEvent(new Event("security-mode-change"));
      setFeedback({ kind: "success", title: "Đã cập nhật chính sách", message: nextPolicy.description });
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể cập nhật chính sách");
      setFeedback({ kind: "error", title: "Không thể cập nhật chính sách", message: error.message });
    } finally {
      setBusy(false);
    }
  };

  const reset = async () => {
    if (!window.confirm("Khôi phục toàn bộ dữ liệu về trạng thái ban đầu?")) return;
    setBusy(true);
    try {
      await request("/demo/reset", { method: "POST" });
      await logout();
    } catch (failure) {
      const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể khôi phục dữ liệu");
      setFeedback({ kind: "error", title: "Không thể khôi phục dữ liệu", message: error.message });
      setBusy(false);
    }
  };

  return <div className="page-stack">
    <header className="page-header"><div><p className="kicker">QUẢN TRỊ HỆ THỐNG</p><h1>Chính sách phê duyệt</h1><p>Thiết lập quy trình kiểm soát giao dịch.</p></div><div className={`security-orb ${mode}`}><small>HIỆN TẠI</small><b>{modePresentation(mode).title}</b></div></header>
    <Feedback value={feedback} onClose={() => setFeedback(null)} />
    <div className="mode-comparison">
      <section className={mode === "baseline" ? "selected" : ""}><span>CHÍNH SÁCH</span><h2>Kiểm soát cơ bản</h2><p>Giao dịch viên có thể hoàn tất giao dịch trong một bước.</p><button className="button warning" disabled={busy || mode === "baseline"} onClick={() => changeMode("baseline")}>Áp dụng kiểm soát cơ bản</button></section>
      <div className="comparison-arrow">→</div>
      <section className={mode === "rbac" ? "selected secure" : "secure"}><span>CHÍNH SÁCH</span><h2>Phân tách nhiệm vụ</h2><p>Giao dịch cần Kiểm soát viên độc lập phê duyệt.</p><button className="button primary" disabled={busy || mode === "rbac"} onClick={() => changeMode("rbac")}>Áp dụng phân tách nhiệm vụ</button></section>
    </div>
    <section className="panel"><div className="section-heading"><div><p className="kicker">DỮ LIỆU HỆ THỐNG</p><h2>Khôi phục dữ liệu</h2></div><button className="button secondary" disabled={busy} onClick={reset}>Khôi phục dữ liệu</button></div></section>
  </div>;
}
