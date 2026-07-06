"use client";

import { FormEvent, useState } from "react";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/Button";

const DEMO_ACCOUNTS = [
  { email: "pm@demo.gov", label: "Program Manager" },
  { email: "projectmanager@demo.gov", label: "Project Manager" },
  { email: "resident-engineer@demo.gov", label: "Resident Engineer" },
  { email: "inspector@demo.gov", label: "Inspector" },
  { email: "designer@demo.gov", label: "Designer" },
  { email: "contractor@demo.gov", label: "Contractor" },
  { email: "executive@demo.gov", label: "DOT Executive" },
];
const DEMO_PASSWORD = "RoadwayDemo!2026";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-1 bg-federal-950">
      <div className="relative hidden flex-1 flex-col justify-between overflow-hidden p-12 text-white lg:flex">
        <Image
          src="/images/hero-construction.jpg"
          alt=""
          fill
          priority
          sizes="50vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-federal-950/85 via-federal-900/75 to-federal-950/95" />

        <div className="relative z-10 flex items-center gap-3">
          <span className="text-3xl">🛣️</span>
          <span className="text-lg font-bold">Roadway AI Inspector &amp; Design Assistant</span>
        </div>
        <div className="relative z-10">
          <h1 className="max-w-md text-4xl font-bold leading-tight drop-shadow-sm">
            AI-powered construction design &amp; inspection for state DOT programs.
          </h1>
          <p className="mt-4 max-w-md text-federal-100/80">
            Document intelligence, inspection reporting, design review, and program dashboards for roadway,
            bridge, pavement, traffic, drainage, and safety workflows.
          </p>
        </div>
        <p className="relative z-10 text-xs text-federal-100/60">
          Delaware DOT Demo Environment — I-95 Corridor Improvement
        </p>
      </div>

      <div className="flex flex-1 items-center justify-center bg-federal-50 p-8">
        <div className="card w-full max-w-sm p-8">
          <h2 className="mb-1 text-xl font-bold text-federal-950">Sign in</h2>
          <p className="mb-6 text-sm text-slate-500">Access your DOT project workspace</p>

          <form onSubmit={handleSubmit}>
            <label className="mb-4 block">
              <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-federal-600 focus:outline-none focus:ring-1 focus:ring-federal-600"
                placeholder="you@demo.gov"
              />
            </label>
            <label className="mb-4 block">
              <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Password
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-federal-600 focus:outline-none focus:ring-1 focus:ring-federal-600"
                placeholder="••••••••"
              />
            </label>

            {error && <p className="mb-4 text-sm text-status-poor">{error}</p>}

            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          <div className="mt-6 border-t border-slate-200 pt-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Demo accounts (password: {DEMO_PASSWORD})
            </p>
            <div className="flex flex-wrap gap-1.5">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.email}
                  type="button"
                  onClick={() => {
                    setEmail(acc.email);
                    setPassword(DEMO_PASSWORD);
                  }}
                  className="rounded-full border border-slate-200 px-2.5 py-1 text-xs text-federal-800 hover:bg-federal-50"
                >
                  {acc.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
