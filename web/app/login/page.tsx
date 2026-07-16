"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "../../components/AuthProvider";
import { ApiError, API_BASE } from "../../lib/api";
import { roleHome } from "../../lib/access";

export default function LoginPage() {
  const router = useRouter();
  const { login, user, ready } = useAuth();
  const [username, setUsername] = useState("admin01");
  const [password, setPassword] = useState("Admin@123");
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

  const useDemoAccount = (account: "admin" | "controller") => {
    if (account === "admin") {
      setUsername("admin01"); setPassword("Admin@123");
    } else {
      setUsername("controller01"); setPassword("Controller@123");
    }
  };

  return (
    <main className="login-screen">
      <section className="login-story">
        <div className="login-brand"><span>N</span>NOVA BANK</div>
        <p className="kicker light">CỔNG VẬN HÀNH NỘI BỘ</p>
        <h1>Một giao dịch.<br />Hai chế độ.<br /><em>Quyền quyết định kết quả.</em></h1>
        <p className="login-lead">Demo nghiệp vụ chuyển khoản 50 triệu trước và sau khi backend áp dụng RBAC.</p>
        <div className="story-steps"><span><b>01</b>Admin tạo giao dịch viên</span><span><b>02</b>Teller tạo yêu cầu</span><span><b>03</b>Controller phê duyệt</span></div>
      </section>
      <section className="login-card">
        <div className="server-line"><i></i>FastAPI · {API_BASE}</div>
        <p className="kicker">PHIÊN ĐĂNG NHẬP THẬT</p><h2>Đăng nhập hệ thống</h2>
        <p>Mật khẩu được xác thực tại backend; mỗi tab giữ một phiên độc lập để chạy demo theo vai trò.</p>
        {expired && <div className="inline-alert warning">Phiên đã hết hạn. Vui lòng đăng nhập lại.</div>}
        <form className="form-grid" onSubmit={submit}>
          <label>Tên đăng nhập<input required value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label>
          <label>Mật khẩu<input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" /></label>
          {error && <div className="inline-alert error">{error}{error.includes("kết nối") && <small>Hãy kiểm tra backend tại http://127.0.0.1:8000/health</small>}</div>}
          <button className="button primary wide" disabled={submitting}>{submitting ? "Đang xác thực…" : "Đăng nhập qua backend"}<span>→</span></button>
        </form>
        <div className="demo-accounts"><span>Tài khoản chuẩn bị sẵn</span><button onClick={() => useDemoAccount("admin")}>Admin</button><button onClick={() => useDemoAccount("controller")}>Controller</button></div>
      </section>
    </main>
  );
}
