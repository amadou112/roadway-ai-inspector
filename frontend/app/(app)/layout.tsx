"use client";

import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/nav/Sidebar";
import { Topbar } from "@/components/nav/Topbar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, error } = useAuth();

  if (error) {
    return (
      <div className="flex min-h-screen flex-1 items-center justify-center bg-federal-50 p-6 text-center">
        <p className="max-w-sm text-sm text-status-poor">{error}</p>
      </div>
    );
  }

  if (loading || !user) {
    return (
      <div className="flex min-h-screen flex-1 items-center justify-center bg-federal-50">
        <p className="text-sm text-slate-400">Loading…</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-1">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto bg-federal-50 p-6">{children}</main>
      </div>
    </div>
  );
}
