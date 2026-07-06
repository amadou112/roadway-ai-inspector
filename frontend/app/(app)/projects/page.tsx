"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { ProjectOut } from "@/lib/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable } from "@/components/ui/DataTable";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Field, TextInput, TextArea } from "@/components/ui/Form";
import { Badge } from "@/components/ui/Badge";

export default function ProjectsPage() {
  const { projects, refresh, selectProject } = useProject();
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: "",
    dot_number: "",
    route: "",
    county: "",
    state: "DE",
    budget: "",
    description: "",
  });

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post<ProjectOut>("/api/v1/projects", {
        ...form,
        budget: Number(form.budget) || 0,
      });
      await refresh();
      setOpen(false);
      setForm({ name: "", dot_number: "", route: "", county: "", state: "DE", budget: "", description: "" });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Projects"
        description="Roadway, bridge, and pavement construction projects in this workspace."
        actions={<Button onClick={() => setOpen(true)}>+ New Project</Button>}
      />

      <DataTable<ProjectOut>
        rows={projects}
        emptyTitle="No projects yet"
        emptyDescription="Create your first project to get started."
        onRowClick={(p) => selectProject(p.id)}
        columns={[
          { header: "Name", render: (p) => <span className="font-medium text-federal-950">{p.name}</span> },
          { header: "Route", render: (p) => p.route || "—" },
          { header: "County", render: (p) => p.county || "—" },
          { header: "Status", render: (p) => <Badge label={p.status} /> },
          { header: "Budget", render: (p) => `$${p.budget.toLocaleString()}` },
        ]}
      />

      <Drawer open={open} onClose={() => setOpen(false)} title="New Project">
        <form onSubmit={handleSubmit}>
          <Field label="Project Name">
            <TextInput required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </Field>
          <Field label="DOT Number">
            <TextInput value={form.dot_number} onChange={(e) => setForm({ ...form, dot_number: e.target.value })} />
          </Field>
          <Field label="Route">
            <TextInput value={form.route} onChange={(e) => setForm({ ...form, route: e.target.value })} />
          </Field>
          <Field label="County">
            <TextInput value={form.county} onChange={(e) => setForm({ ...form, county: e.target.value })} />
          </Field>
          <Field label="Budget (USD)">
            <TextInput
              type="number"
              value={form.budget}
              onChange={(e) => setForm({ ...form, budget: e.target.value })}
            />
          </Field>
          <Field label="Description">
            <TextArea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </Field>
          <Button type="submit" className="w-full" disabled={saving}>
            {saving ? "Creating…" : "Create Project"}
          </Button>
        </form>
      </Drawer>
    </div>
  );
}
