"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, loading, error } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading || error) return;
    if (user) router.replace("/dashboard");
  }, [loading, error, user, router]);

  return (
    <div className="flex min-h-screen flex-1 flex-col items-center justify-center gap-3 bg-federal-950 text-white">
      <p className="text-sm text-federal-100/70">
        {error || "Loading Roadway AI Inspector & Design Assistant…"}
      </p>
    </div>
  );
}
