"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { useAuth } from "../../../../components/AuthProvider";
import { Feedback } from "../../../../components/Feedback";
import { roleLabels } from "../../../../lib/access";
import { ApiError } from "../../../../lib/api";
import type { FeedbackState, ManagedUser, Role } from "../../../../lib/types";

const initialUser = { username: "lan.demo", display_name: "Lan Nguyễn", password: "Lan@1234", role: "teller" };

export default function UsersPage() {
  const { request } = useAuth();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [form, setForm] = useState(initialUser);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackState | null>(null);
  const refresh = useCallback(async () => {
    try {
      const [people, available] = await Promise.all([request<ManagedUser[]>("/users"), request<Role[]>("/roles")]);
      setUsers(people); setRoles(available);
    } catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tải nhân viên"); setFeedback({ kind: "error", title: "Không thể tải dữ liệu", message: error.message }); }
  }, [request]);
  useEffect(() => { refresh(); }, [refresh]);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setSubmitting(true); setFeedback(null);
    try {
      await request("/users", { method: "POST", body: JSON.stringify(form) });
      setFeedback({ kind: "success", title: "Đã tạo tài khoản", message: `${form.username} đã được gán vai trò ${roleLabels[form.role]}.` });
      await refresh();
    } catch (failure) { const error = failure instanceof ApiError ? failure : new ApiError(0, "Không thể tạo tài khoản"); setFeedback({ kind: "error", title: "Không thể tạo tài khoản", message: error.message }); }
    finally { setSubmitting(false); }
  };
  return <div className="page-stack"><header className="page-header"><div><p className="kicker">QUẢN TRỊ TRUY CẬP</p><h1>Nhân viên và vai trò</h1><p>Quản lý tài khoản và phân công vai trò nghiệp vụ.</p></div><div className="header-stat"><small>NHÂN VIÊN</small><b>{users.length}</b></div></header><Feedback value={feedback} onClose={() => setFeedback(null)} /><div className="two-panel"><section className="panel"><div className="section-heading"><div><p className="kicker">THÊM NHÂN VIÊN</p><h2>Tài khoản mới</h2></div></div><form className="form-grid two-columns" onSubmit={submit}><label>Họ và tên<input required value={form.display_name} onChange={(event) => setForm({ ...form, display_name: event.target.value })} /></label><label>Tên đăng nhập<input required pattern="[a-zA-Z0-9_.-]{3,40}" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label><label>Mật khẩu tạm<input required type="password" minLength={8} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label><label>Vai trò<select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })}>{roles.map((role) => <option key={role} value={role}>{roleLabels[role] ?? role}</option>)}</select></label><button className="button primary full-field" disabled={submitting}>{submitting ? "Đang tạo…" : "Tạo tài khoản và gán vai trò"}<span>→</span></button></form></section><section className="panel"><div className="section-heading"><div><p className="kicker">DANH SÁCH HIỆN TẠI</p><h2>Danh sách nhân viên</h2></div></div><div className="user-list">{users.map((person) => <div key={person.username}><span className="avatar">{person.display_name.split(" ").at(-1)?.[0]}</span><div><b>{person.display_name}</b><small>{person.username}</small></div><em>{person.roles.map((role) => roleLabels[role] ?? role).join(", ")}</em></div>)}</div></section></div></div>;
}
