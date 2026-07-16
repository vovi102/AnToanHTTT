"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "../../../components/AuthProvider";
import { Feedback } from "../../../components/Feedback";
import { formatDateTime } from "../../../lib/transactions";
import { ApiError } from "../../../lib/api";
import type { AuditEvent, FeedbackState } from "../../../lib/types";

export default function AuditPage() {
  const { request } = useAuth();
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [outcome, setOutcome] = useState("all");
  const [query, setQuery] = useState("");
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const refresh = useCallback(async () => {
    try { setEvents(await request<AuditEvent[]>("/audit-logs")); }
    catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải audit log"); setFeedback({ kind: "error", title: "Không thể tải nhật ký", message: error.message }); }
  }, [request]);
  useEffect(() => { refresh(); }, [refresh]);
  const filtered = useMemo(() => events.filter((event) => {
    if (outcome !== "all" && event.outcome !== outcome) return false;
    const text = `${event.username} ${event.role_at_event} ${event.resource} ${event.action} ${event.transaction_reference} ${event.detail}`.toLowerCase();
    return text.includes(query.toLowerCase());
  }), [events, outcome, query]);
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">BẰNG CHỨNG BACKEND</p><h1>Nhật ký kiểm toán</h1><p>Mọi quyết định cho phép, bypass, từ chối và thay đổi trạng thái từ SQLite.</p></div><div className="header-stat"><small>SỰ KIỆN</small><b>{events.length}</b></div></header><Feedback value={feedback} onClose={() => setFeedback(null)} /><section className="panel"><div className="audit-filters"><label>Tìm kiếm<input placeholder="Actor, giao dịch, hành động…" value={query} onChange={(event) => setQuery(event.target.value)} /></label><label>Kết quả<select value={outcome} onChange={(event) => setOutcome(event.target.value)}><option value="all">Tất cả</option><option value="baseline_bypass">Baseline bypass</option><option value="denied">Denied</option><option value="allowed">Allowed</option><option value="success">Success</option><option value="conflict">Conflict</option></select></label><button className="button secondary" onClick={refresh}>Tải lại</button></div><div className="audit-table"><div className="audit-row audit-header"><span>Thời gian</span><span>Người thực hiện</span><span>Hành động</span><span>Giao dịch</span><span>Kết quả</span></div>{filtered.map((event) => <div className="audit-row" key={event.id}><span>{formatDateTime(event.created_at)}</span><span><b>{event.username ?? "anonymous"}</b><small>{event.role_at_event ?? "—"}</small></span><span><b>{event.resource}:{event.action}</b><small>{event.detail}</small></span><span><code>{event.transaction_reference ?? "—"}</code></span><span><em className={`outcome outcome-${event.outcome}`}>{event.outcome}</em></span></div>)}</div>{!filtered.length && <div className="empty-state">Không có sự kiện phù hợp bộ lọc.</div>}</section></div>;
}
