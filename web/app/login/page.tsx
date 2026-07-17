"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "../../components/AuthProvider";
import { ApiError } from "../../lib/api";
import { roleHome } from "../../lib/access";

export default function LoginPage() {
  const router = useRouter();
  const { login, user, ready } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    setExpired(new URLSearchParams(window.location.search).get("reason") === "expired");
  }, []);

  useEffect(() => {
    if (ready && user) router.replace(roleHome(user.roles));
  }, [ready, router, user]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const current = await login(username, password);
      router.replace(roleHome(current.roles));
    } catch (failure) {
      setError(failure instanceof ApiError ? failure.message : "Không thể đăng nhập");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="login-screen">
      <section className="login-story">
        <div className="login-brand"><span>N</span>NOVA BANK</div>
        <p className="kicker light">CỔNG NGHIỆP VỤ NỘI BỘ</p>
        <h1>Vận hành giao dịch<br /><em>an toàn và nhất quán.</em></h1>
        <p className="login-lead">Không gian làm việc dành cho nhân viên Nova Bank.</p>
      </section>
      <section className="login-card">
        <p className="kicker">ĐĂNG NHẬP HỆ THỐNG</p><h2>Đăng nhập hệ thống</h2>
        <p>Sử dụng tài khoản nội bộ đã được cấp.</p>
        {expired && <div className="inline-alert warning">Phiên đã hết hạn. Vui lòng đăng nhập lại.</div>}
        <form className="form-grid" onSubmit={submit}>
          <label>Tên đăng nhập<input required value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label>
          <label>Mật khẩu<input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" /></label>
          {error && <div className="inline-alert error">{error}</div>}
          <button className="button primary wide" disabled={submitting}>{submitting ? "Đang đăng nhập…" : "Đăng nhập"}<span>→</span></button>
        </form>
      </section>
    </main>
  );
}
