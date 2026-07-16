"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "../components/AuthProvider";
import { roleHome } from "../lib/access";

export default function HomePage() {
  const router = useRouter();
  const { ready, user } = useAuth();

  useEffect(() => {
    if (!ready) return;
    router.replace(user ? roleHome(user.roles) : "/login");
  }, [ready, router, user]);

  return <main className="loading-screen">Đang mở cổng vận hành…</main>;
}
