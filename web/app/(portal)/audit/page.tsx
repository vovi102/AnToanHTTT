"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "../../../components/AuthProvider";
import { Feedback } from "../../../components/Feedback";
import { roleLabels } from "../../../lib/access";
import { auditActionLabel, auditOutcomeLabel } from "../../../lib/presentation";
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
    const text = `${event.username} ${roleLabels[event.role_at_event ?? ""] ?? "Hệ thống"} ${auditActionLabel(event.resource, event.action)} ${event.transaction_reference}`.toLowerCase();
    return text.includes(query.toLowerCase());
  }), [events, outcome, query]);
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">GIÁM SÁT HỆ THỐNG</p><h1>Lịch sử hoạt động</h1><p>Theo dõi các thay đổi và quyết định truy cập trong hệ thống.</p></div><div className="header-stat"><small>SỰ KIỆN</small><b>{events.length}</b></div></header><Feedback value={feedback} onClose={() => setFeedback(null)} /><section className="panel"><div className="audit-filters"><label>Tìm kiếm<input placeholder="Người thực hiện, giao dịch, hành động…" value={query} onChange={(event) => setQuery(event.target.value)} /></label><label>Kết quả<select value={outcome} onChange={(event) => setOutcome(event.target.value)}><option value="all">Tất cả</option>{["baseline_bypass", "denied", "allowed", "success", "failed", "conflict"].map((value) => <option key={value} value={value}>{auditOutcomeLabel(value)}</option>)}</select></label><button className="button secondary" onClick={refresh}>Tải lại</button></div><div className="audit-table"><div className="audit-row audit-header"><span>Thời gian</span><span>Người thực hiện</span><span>Hành động</span><span>Giao dịch</span><span>Kết quả</span></div>{filtered.map((event) => <div className="audit-row" key={event.id}><span>{formatDateTime(event.created_at)}</span><span><b>{event.username ?? "Hệ thống"}</b><small>{roleLabels[event.role_at_event ?? ""] ?? "Hệ thống"}</small></span><span><b>{auditActionLabel(event.resource, event.action)}</b></span><span><code>{event.transaction_reference ?? "—"}</code></span><span><em className={`outcome outcome-${event.outcome}`}>{auditOutcomeLabel(event.outcome)}</em></span></div>)}</div>{!filtered.length && <div className="empty-state">Không có sự kiện phù hợp bộ lọc.</div>}</section></div>;
}
