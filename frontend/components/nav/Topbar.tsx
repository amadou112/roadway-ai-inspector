"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useProject } from "@/lib/project-context";
import { DEMO_ACCOUNTS } from "@/lib/demo-accounts";

const ROLE_LABELS: Record<string, string> = {
  program_manager: "Program Manager",
  project_manager: "Project Manager",
  resident_engineer: "Resident Engineer",
  inspector: "Inspector",
  designer: "Designer",
  contractor: "Contractor",
  dot_executive: "DOT Executive",
};

export function Topbar() {
  const { user, switchRole } = useAuth();
  const { projects, selectedProject, selectProject } = useProject();
  const [switching, setSwitching] = useState(false);

  async function handleRoleChange(email: string) {
    setSwitching(true);
    try {
      await switchRole(email);
    } finally {
      setSwitching(false);
    }
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Project</span>
        <select
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-federal-900 focus:outline-none focus:ring-1 focus:ring-federal-600"
          value={selectedProject?.id || ""}
          onChange={(e) => selectProject(e.target.value)}
        >
          {projects.length === 0 && <option value="">No projects</option>}
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Viewing as</span>
        <select
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-federal-900 focus:outline-none focus:ring-1 focus:ring-federal-600 disabled:opacity-50"
          value={user?.email || ""}
          disabled={switching}
          onChange={(e) => handleRoleChange(e.target.value)}
        >
          {DEMO_ACCOUNTS.map((acc) => (
            <option key={acc.email} value={acc.email}>
              {acc.label}
            </option>
          ))}
        </select>
        <div className="text-right leading-tight">
          <p className="text-sm font-semibold text-federal-950">{user?.full_name}</p>
          <p className="text-xs text-slate-400">{user ? ROLE_LABELS[user.role] : ""}</p>
        </div>
      </div>
    </header>
  );
}
