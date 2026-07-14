"use client";

import { FormEvent, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type User = { username: string; display_name: string; roles: string[] };
type Account = { id: number; customer_name: string; phone: string; address: string };
type Audit = { created_at: string; username: string | null; resource: string; action: string; outcome: string; detail: string };
type Proof = { endpoint: string; status: number; message: string; permission?: string; success: boolean };

class ApiError extends Error {
  constructor(public status: number, message: string, public permission?: string) { super(message); }
}

async function request<T>(path: string, token?: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    throw new ApiError(response.status, typeof detail === "object" ? detail.message : detail || "Yêu cầu thất bại", typeof detail === "object" ? detail.permission : undefined);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

const roleLabel: Record<string, string> = { administrator: "Quản trị viên", teller: "Giao dịch viên", auditor: "Kiểm toán viên" };

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [username, setUsername] = useState("admin01");
  const [password, setPassword] = useState("Admin@123");
  const [loginError, setLoginError] = useState("");
  const [proof, setProof] = useState<Proof | null>(null);
  const [tab, setTab] = useState("overview");
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [users, setUsers] = useState<Array<{ username: string; display_name: string; status: string; roles: string[] }>>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [newUser, setNewUser] = useState({ username: "", display_name: "", password: "Demo@123", role: "teller" });

  useEffect(() => {
    const saved = sessionStorage.getItem("banksafe_token");
    if (!saved) return;
    request<User>("/auth/me", saved).then((me) => { setToken(saved); setUser(me); }).catch(() => sessionStorage.removeItem("banksafe_token"));
  }, []);

  const showSuccess = (endpoint: string, message: string) => setProof({ endpoint, status: 200, message, success: true });
  const showError = (endpoint: string, error: unknown) => {
    const apiError = error instanceof ApiError ? error : new ApiError(0, "Không thể kết nối backend FastAPI");
    setProof({ endpoint, status: apiError.status, message: apiError.message, permission: apiError.permission, success: false });
  };

  const signIn = async (event: FormEvent) => {
    event.preventDefault(); setLoginError("");
    try {
      const result = await request<{ token: string; user: User }>("/auth/login", undefined, { method: "POST", body: JSON.stringify({ username, password }) });
      sessionStorage.setItem("banksafe_token", result.token); setToken(result.token); setUser(result.user); showSuccess("POST /auth/login", "Mật khẩu đã được backend xác thực và phiên đã được tạo.");
    } catch (error) { setLoginError(error instanceof Error ? error.message : "Không thể đăng nhập"); }
  };

  const loadAccounts = async () => {
    try { const data = await request<Account[]>("/accounts", token!); setAccounts(data); setTab("accounts"); showSuccess("GET /accounts", "Backend cho phép đọc dữ liệu khách hàng."); }
    catch (error) { showError("GET /accounts", error); }
  };
  const loadUsers = async () => {
    try { const [people, availableRoles] = await Promise.all([request<typeof users>("/users", token!), request<string[]>("/roles", token!)]); setUsers(people); setRoles(availableRoles); setTab("users"); showSuccess("GET /users", "Backend xác nhận quyền users:manage."); }
    catch (error) { showError("GET /users", error); }
  };
  const loadAudit = async () => {
    try { const data = await request<Audit[]>("/audit-logs", token!); setAudit(data); setTab("audit"); showSuccess("GET /audit-logs", "Backend xác nhận quyền audit_logs:read và trả audit log từ SQLite."); }
    catch (error) { showError("GET /audit-logs", error); }
  };
  const createUser = async (event: FormEvent) => {
    event.preventDefault();
    try { await request("/users", token!, { method: "POST", body: JSON.stringify(newUser) }); showSuccess("POST /users", `Đã tạo ${newUser.username} với role ${roleLabel[newUser.role]}. Hãy đăng xuất rồi đăng nhập thử.`); await loadUsers(); setNewUser({ username: "", display_name: "", password: "Demo@123", role: "teller" }); }
    catch (error) { showError("POST /users", error); }
  };
  const saveAccount = async (account: Account) => {
    try { await request(`/accounts/${account.id}`, token!, { method: "PATCH", body: JSON.stringify({ phone: account.phone, address: account.address }) }); showSuccess(`PATCH /accounts/${account.id}`, "Thông tin khách hàng đã được cập nhật thật trong SQLite."); await loadAccounts(); }
    catch (error) { showError(`PATCH /accounts/${account.id}`, error); }
  };
  const reset = async () => {
    try { await request("/demo/reset", token!, { method: "POST" }); sessionStorage.removeItem("banksafe_token"); setToken(null); setUser(null); setProof({ endpoint: "POST /demo/reset", status: 200, message: "Dữ liệu đã được đặt lại. Phiên cũ bị vô hiệu hóa.", success: true }); }
    catch (error) { showError("POST /demo/reset", error); }
  };
  const signOut = async () => { if (token) await request("/auth/logout", token, { method: "POST" }).catch(() => undefined); sessionStorage.removeItem("banksafe_token"); setToken(null); setUser(null); };

  if (!user) return <main className="login-page"><section className="login-copy"><div className="brand"><span className="brand-mark">B</span> BankSafe</div><p className="eyebrow">RBAC + BACKEND THẬT</p><h1>Tạo người dùng.<br />Gán vai trò.<br /><em>Kiểm tra ở server.</em></h1><p className="lead">Mỗi đăng nhập, thao tác và lần từ chối đều đi qua FastAPI và được lưu vào SQLite audit log.</p><div className="login-steps"><span><b>01</b> Admin tạo tài khoản và role</span><span><b>02</b> Nhân viên đăng nhập bằng mật khẩu</span><span><b>03</b> API kiểm tra quyền cho từng request</span></div></section><section className="login-panel"><div className="panel-top"><span className="lock">⌁</span><span>BankSafe Internal · API {API_BASE}</span></div><h2>Đăng nhập</h2><p>Bắt đầu bằng tài khoản quản trị mẫu để tạo nhân viên: <b>admin01 / Admin@123</b>.</p><form className="form" onSubmit={signIn}><label>Tên đăng nhập<input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" /></label><label>Mật khẩu<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" /></label>{loginError && <p className="form-error">{loginError}</p>}<button className="primary" type="submit">Đăng nhập qua backend <span>→</span></button></form></section></main>;

  const role = user.roles[0] || "";
  return <main className="app-shell"><aside className="sidebar"><div className="brand"><span className="brand-mark">B</span> BankSafe</div><div className="person"><span className="avatar">{user.display_name.split(" ").map((part) => part[0]).slice(-2).join("")}</span><div><b>{user.display_name}</b><small>{roleLabel[role] || role}</small></div></div><nav><button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>⌂ Tổng quan</button><button onClick={loadAccounts}>▣ Khách hàng</button><button onClick={loadUsers}>♙ Quản lý người dùng</button><button onClick={loadAudit}>◫ Nhật ký kiểm toán</button></nav><button className="signout" onClick={signOut}>← Đăng xuất</button></aside><section className="workspace"><header><div><p className="eyebrow">PHIÊN ĐĂNG NHẬP THẬT</p><h1>Chào, {user.display_name.split(" ").at(-1)}.</h1></div><div className="secure">✓ {roleLabel[role] || role}</div></header><section className="journey"><div className="journey-heading"><b>Luồng đã xảy ra ở backend</b><span>SQLite + FastAPI</span></div><div className="journey-rail"><div className="step done"><i>1</i><span>Đăng nhập</span><small>{user.username}</small></div><div className="line"/><div className="step done"><i>2</i><span>Vai trò</span><small>{role}</small></div><div className="line"/><div className="step current"><i>3</i><span>API kiểm tra</span><small>mỗi request</small></div></div></section>{proof && <section className={`proof ${proof.success ? "success" : "failure"}`}><b>{proof.success ? "✓ API cho phép" : "× API chặn"}</b><span><code>{proof.endpoint}</code> → HTTP {proof.status}{proof.permission ? ` · cần ${proof.permission}` : ""}<br />{proof.message}</span></section>}{tab === "overview" && <section className="grid"><div className="card"><p className="eyebrow">VAI TRÒ ĐANG DÙNG</p><h2>{roleLabel[role] || role}</h2><p>Hãy mở <b>Quản lý người dùng</b>. Nếu bạn không phải admin, giao diện vẫn gọi API và backend sẽ trả 403 — bằng chứng bảo vệ không nằm ở nút bấm.</p><button className="action" onClick={loadUsers}>Thử quản lý người dùng <span>→</span></button></div><div className="card logic"><p className="eyebrow">DEMO THỰC HÀNH</p><h2>1. Login admin</h2><p>2. Tạo “Lan demo” role Teller.<br />3. Logout, login Lan.<br />4. Cập nhật khách hàng rồi thử quản lý user.</p></div></section>}{tab === "users" && <section className="stack"><div className="card"><p className="eyebrow">TẠO NHÂN VIÊN MỚI</p><h2>Gán role khi tạo tài khoản</h2><form className="form compact" onSubmit={createUser}><label>Họ tên<input required value={newUser.display_name} onChange={(e) => setNewUser({ ...newUser, display_name: e.target.value })}/></label><label>Username<input required value={newUser.username} onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}/></label><label>Mật khẩu tạm<input required type="password" value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}/></label><label>Role<select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>{(roles.length ? roles : ["administrator", "teller", "auditor"]).map((item) => <option key={item} value={item}>{roleLabel[item] || item}</option>)}</select></label><button className="primary" type="submit">Tạo tài khoản <span>→</span></button></form></div><div className="card"><p className="eyebrow">DANH SÁCH TỪ SQLITE</p><h2>Người dùng và role</h2><div className="table">{users.map((item) => <div key={item.username}><b>{item.display_name}</b><span>{item.username}</span><em>{item.roles.map((r) => roleLabel[r]).join(", ")}</em></div>)}</div><button className="danger" onClick={reset}>Đặt lại dữ liệu demo</button></div></section>}{tab === "accounts" && <section className="stack"><div className="card"><p className="eyebrow">DỮ LIỆU TỪ SQLITE</p><h2>Tài khoản khách hàng</h2>{accounts.length === 0 ? <button className="action" onClick={loadAccounts}>Tải dữ liệu khách hàng <span>→</span></button> : <div className="account-list">{accounts.map((account) => <AccountEditor key={account.id} account={account} onSave={saveAccount}/>)}</div>}</div></section>}{tab === "audit" && <section className="card"><p className="eyebrow">BẰNG CHỨNG BACKEND</p><h2>Audit log</h2>{audit.length === 0 ? <button className="action" onClick={loadAudit}>Tải audit log <span>→</span></button> : <div className="table audit">{audit.map((item, index) => <div key={`${item.created_at}-${index}`}><b className={item.outcome === "denied" || item.outcome === "failed" ? "red" : "green"}>{item.outcome.toUpperCase()}</b><span>{item.username || "anonymous"} · {item.resource}:{item.action}</span><em>{item.detail}</em></div>)}</div>}</section>}</section></main>;
}

function AccountEditor({ account, onSave }: { account: Account; onSave: (account: Account) => void }) {
  const [draft, setDraft] = useState(account);
  return <div className="account"><b>{draft.customer_name}</b><label>Số điện thoại<input value={draft.phone} onChange={(e) => setDraft({ ...draft, phone: e.target.value })}/></label><label>Địa chỉ<input value={draft.address} onChange={(e) => setDraft({ ...draft, address: e.target.value })}/></label><button className="action" onClick={() => onSave(draft)}>Lưu thay đổi <span>→</span></button></div>;
}
