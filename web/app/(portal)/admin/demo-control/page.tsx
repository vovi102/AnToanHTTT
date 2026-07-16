"use client";

import { useCallback, useEffect, useState } from "react";

import { useAuth } from "../../../../components/AuthProvider";
import { Feedback } from "../../../../components/Feedback";
import { ApiError } from "../../../../lib/api";
import type { FeedbackState, SecurityMode } from "../../../../lib/types";

export default function DemoControlPage() {
  const { request, logout } = useAuth();
  const [mode, setMode] = useState<SecurityMode>("baseline");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const refresh = useCallback(async () => { try { setMode((await request<{ mode: SecurityMode }>("/demo/security-mode")).mode); } catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải chế độ"); setFeedback({ kind: "error", title: "Không thể tải cấu hình", message: error.message }); } }, [request]);
  useEffect(() => { refresh(); }, [refresh]);
  const changeMode = async (next: SecurityMode) => {
    if (next === mode || !window.confirm(`Chuyển hệ thống sang ${next === "rbac" ? "RBAC" : "Baseline"}?`)) return;
    setBusy(true);
    try {
      await request("/demo/security-mode", { method: "PATCH", body: JSON.stringify({ mode: next }) });
      setMode(next); window.dispatchEvent(new Event("security-mode-change"));
      setFeedback({ kind: "success", title: next === "rbac" ? "RBAC đã được bật" : "Đã về Baseline", message: next === "rbac" ? "Request phê duyệt của Teller bây giờ sẽ được kiểm tra tại backend." : "Chỉ quyền phê duyệt giao dịch được bypass để so sánh." });
    } catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể đổi chế độ"); setFeedback({ kind: "error", title: "Không thể đổi chế độ", message: error.message }); }
    finally { setBusy(false); }
  };
  const reset = async () => {
    if (!window.confirm("Xóa toàn bộ dữ liệu demo và khôi phục hai tài khoản chuẩn bị sẵn?")) return;
    setBusy(true);
    try { await request("/demo/reset", { method: "POST" }); await logout(); }
    catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể đặt lại demo"); setFeedback({ kind: "error", title: "Không thể đặt lại", message: error.message }); setBusy(false); }
  };
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">BẢNG ĐIỀU KHIỂN TRÌNH DIỄN</p><h1>Trước và sau RBAC</h1><p>Chỉ Admin thay đổi được chính sách; thao tác được ghi vào audit log.</p></div><div className={`security-orb ${mode}`}><small>HIỆN TẠI</small><b>{mode === "rbac" ? "RBAC" : "BASELINE"}</b></div></header><Feedback value={feedback} onClose={() => setFeedback(null)} /><div className="mode-comparison"><section className={mode === "baseline" ? "selected" : ""}><span>01 · TRƯỚC RBAC</span><h2>Baseline</h2><p>Giao dịch viên có thể tạo rồi tự phê duyệt giao dịch 50 triệu.</p><ul><li>Vẫn xác thực người dùng</li><li>Bypass quyền duyệt để so sánh</li><li>Ghi audit `baseline_bypass`</li></ul><button className="button warning" disabled={busy || mode === "baseline"} onClick={() => changeMode("baseline")}>Chuyển sang Baseline</button></section><div className="comparison-arrow">→</div><section className={mode === "rbac" ? "selected secure" : "secure"}><span>02 · SAU RBAC</span><h2>RBAC</h2><p>Cùng tài khoản Teller bị backend chặn; Controller mới được duyệt.</p><ul><li>Permission `transactions:approve`</li><li>HTTP 403, không đổi dữ liệu</li><li>Controller hoàn tất giao dịch</li></ul><button className="button primary" disabled={busy || mode === "rbac"} onClick={() => changeMode("rbac")}>Bật bảo vệ RBAC</button></section></div><section className="panel demo-journey"><div><p className="kicker">KỊCH BẢN 5 BƯỚC</p><h2>Tiến trình trình bày</h2></div><ol><li><b>Admin</b><span>Tạo `lan.demo` role Teller</span></li><li><b>Teller · Baseline</b><span>Tạo và tự duyệt giao dịch thứ nhất</span></li><li><b>Admin</b><span>Bật bảo vệ RBAC</span></li><li><b>Teller · RBAC</b><span>Tạo giao dịch thứ hai, thử request và nhận 403</span></li><li><b>Controller</b><span>Phê duyệt giao dịch đang chờ</span></li></ol><button className="text-danger" disabled={busy} onClick={reset}>Đặt lại toàn bộ dữ liệu demo</button></section></div>;
}
