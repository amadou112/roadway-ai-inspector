"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    router.replace(user ? "/dashboard" : "/login");
  }, [loading, user, router]);

  return (
    <div className="flex min-h-screen flex-1 items-center justify-center bg-federal-950 text-white">
      <p className="text-sm text-federal-100/70">Loading Roadway AI Inspector &amp; Design Assistant…</p>
    </div>
  );
}
