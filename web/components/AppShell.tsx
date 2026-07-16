"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { navigationFor, roleHome, roleLabels } from "../lib/access";
import type { SecurityMode } from "../lib/types";
import { useAuth } from "./AuthProvider";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, ready, logout, request } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [mode, setMode] = useState<SecurityMode>("baseline");

  useEffect(() => {
    if (ready && !user) router.replace("/login");
  }, [ready, router, user]);

  useEffect(() => {
    if (!user) return;
    const refresh = () => request<{ mode: SecurityMode }>("/demo/security-mode")
      .then((result) => setMode(result.mode))
      .catch(() => undefined);
    refresh();
    window.addEventListener("focus", refresh);
    return () => window.removeEventListener("focus", refresh);
  }, [request, user]);

  if (!ready || !user) return <main className="loading-screen">Đang kiểm tra phiên đăng nhập…</main>;
  const navigation = navigationFor(user.roles);
  const role = user.roles[0] ?? "";

  return (
    <main className="portal-shell">
      <aside className="portal-sidebar">
        <Link className="portal-brand" href={roleHome(user.roles)}><span>N</span>NOVA BANK</Link>
        <div className="actor-card"><b>{user.display_name}</b><small>{roleLabels[role] ?? role}</small></div>
        <nav>{navigation.map((item) => (
          <Link key={item.href} className={pathname === item.href ? "active" : ""} href={item.href}>
            <i>{item.shortLabel}</i>{item.label}
          </Link>
        ))}</nav>
        <button className="logout-button" type="button" onClick={() => logout()}>Đăng xuất</button>
      </aside>
      <section className="portal-workspace">
        <div className={`mode-banner mode-${mode}`}>
          <div><strong>{mode === "rbac" ? "RBAC đang bảo vệ hệ thống" : "Baseline — chưa áp dụng RBAC"}</strong>
          <span>{mode === "rbac" ? "Backend kiểm tra quyền trên từng thao tác nhạy cảm" : "Chế độ so sánh chỉ dùng trong buổi demo"}</span></div>
          <b>{mode === "rbac" ? "SECURE MODE" : "BASELINE"}</b>
        </div>
        {children}
      </section>
    </main>
  );
}
