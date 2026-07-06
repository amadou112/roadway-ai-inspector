"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { PageHeader, EmptyState } from "@/components/ui/PageHeader";
import { DataTable, Column } from "@/components/ui/DataTable";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Field, TextInput, TextArea, Select } from "@/components/ui/Form";

export interface FormFieldConfig {
  name: string;
  label: string;
  type: "text" | "textarea" | "select" | "number" | "date";
  options?: { value: string; label: string }[];
  required?: boolean;
}

interface EntityBase {
  id: string;
}

export interface EntityHelpers {
  updateField: (id: string, field: string, value: string) => Promise<void>;
}

export function EntityCrudPage<T extends EntityBase>({
  title,
  description,
  endpointBase,
  columns,
  formFields,
  defaultForm,
  createLabel = "+ New",
}: {
  title: string;
  description: string;
  endpointBase: (projectId: string) => string;
  columns: Column<T>[] | ((helpers: EntityHelpers) => Column<T>[]);
  formFields: FormFieldConfig[];
  defaultForm: Record<string, string>;
  createLabel?: string;
}) {
  const { selectedProject, loading: projectLoading } = useProject();
  const [rows, setRows] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, string>>(defaultForm);

  async function load() {
    if (!selectedProject) {
      setRows([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await api.get<T[]>(endpointBase(selectedProject.id));
      setRows(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProject]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!selectedProject) return;
    setSaving(true);
    setError(null);
    try {
      const payload: Record<string, unknown> = {};
      for (const field of formFields) {
        const value = form[field.name];
        if (field.type === "number") payload[field.name] = value ? Number(value) : 0;
        else payload[field.name] = value || null;
      }
      await api.post(endpointBase(selectedProject.id), payload);
      await load();
      setOpen(false);
      setForm(defaultForm);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  if (projectLoading || loading) {
    return <p className="text-sm text-slate-400">Loading…</p>;
  }

  if (!selectedProject) {
    return <EmptyState title="No project selected" description="Select a project from the top bar first." />;
  }

  async function updateField(id: string, field: string, value: string) {
    if (!selectedProject) return;
    const updated = await api.patch<T>(`${endpointBase(selectedProject.id)}/${id}`, { [field]: value });
    setRows((prev) => prev.map((r) => (r.id === id ? updated : r)));
  }

  const resolvedColumns = typeof columns === "function" ? columns({ updateField }) : columns;

  return (
    <div>
      <PageHeader
        title={title}
        description={description}
        actions={<Button onClick={() => setOpen(true)}>{createLabel}</Button>}
      />

      <DataTable<T> rows={rows} columns={resolvedColumns} />

      <Drawer open={open} onClose={() => setOpen(false)} title={createLabel.replace("+ ", "")}>
        <form onSubmit={handleSubmit}>
          {formFields.map((field) => (
            <Field key={field.name} label={field.label}>
              {field.type === "textarea" ? (
                <TextArea
                  required={field.required}
                  value={form[field.name] || ""}
                  onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
                />
              ) : field.type === "select" ? (
                <Select
                  required={field.required}
                  value={form[field.name] || ""}
                  onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
                >
                  {field.options?.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              ) : (
                <TextInput
                  type={field.type}
                  required={field.required}
                  value={form[field.name] || ""}
                  onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
                />
              )}
            </Field>
          ))}
          {error && <p className="mb-4 text-sm text-status-poor">{error}</p>}
          <Button type="submit" className="w-full" disabled={saving}>
            {saving ? "Saving…" : "Save"}
          </Button>
        </form>
      </Drawer>
    </div>
  );
}

export function InlineSelect({
  value,
  options,
  onChange,
}: {
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => {
        e.stopPropagation();
        onChange(e.target.value);
      }}
      onClick={(e) => e.stopPropagation()}
      className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs capitalize"
    >
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {opt.replace(/_/g, " ")}
        </option>
      ))}
    </select>
  );
}

export function CardValue({ children }: { children: ReactNode }) {
  return <span className="text-sm text-slate-700">{children}</span>;
}
