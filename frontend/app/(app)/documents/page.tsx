"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DocumentOut, DocType } from "@/lib/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable } from "@/components/ui/DataTable";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Field, TextInput, Select } from "@/components/ui/Form";
import { Badge } from "@/components/ui/Badge";

const DOC_TYPES: { value: DocType; label: string }[] = [
  { value: "spec", label: "DOT Specification" },
  { value: "fhwa_manual", label: "FHWA Manual" },
  { value: "inspection_report", label: "Inspection Report" },
  { value: "rfi", label: "RFI" },
  { value: "submittal", label: "Submittal" },
  { value: "plan_sheet", label: "Plan Sheet" },
  { value: "daily_report", label: "Daily Report" },
  { value: "other", label: "Other" },
];

export default function DocumentsPage() {
  const { selectedProject, loading: projectLoading } = useProject();
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [docType, setDocType] = useState<DocType>("spec");
  const [file, setFile] = useState<File | null>(null);

  async function load() {
    if (!selectedProject) return setLoading(false);
    setLoading(true);
    try {
      const data = await api.get<DocumentOut[]>(`/api/v1/projects/${selectedProject.id}/documents`);
      setDocs(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProject]);

  async function handleUpload(e: FormEvent) {
    e.preventDefault();
    if (!selectedProject || !file) return;
    setUploading(true);
    setError(null);
    try {
      const form = new FormData();
      form.set("title", title);
      form.set("doc_type", docType);
      form.set("file", file);
      await api.postForm(`/api/v1/projects/${selectedProject.id}/documents`, form);
      await load();
      setOpen(false);
      setTitle("");
      setFile(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  if (projectLoading || loading) return <p className="text-sm text-slate-400">Loading…</p>;

  return (
    <div>
      <PageHeader
        title="Document Library"
        description="Specifications, FHWA manuals, inspection reports, RFIs, submittals, plan sheets, and daily reports."
        actions={<Button onClick={() => setOpen(true)}>+ Upload Document</Button>}
      />

      <Card className="mb-4">
        <p className="text-xs text-slate-500">
          Uploaded documents are automatically chunked and embedded for the AI Assistant. Ask questions in the{" "}
          <span className="font-semibold text-federal-900">AI Assistant</span> tab and get cited answers.
        </p>
      </Card>

      <DataTable<DocumentOut>
        rows={docs}
        emptyTitle="No documents uploaded yet"
        emptyDescription="Upload a spec, manual, or report to enable the AI Assistant."
        columns={[
          { header: "Title", render: (d) => <span className="font-medium text-federal-950">{d.title}</span> },
          { header: "Type", render: (d) => <Badge label={d.doc_type} tone="blue" /> },
          { header: "Status", render: (d) => <Badge label={d.status} /> },
          { header: "Pages", render: (d) => d.page_count },
          { header: "Chunks", render: (d) => d.chunk_count },
          { header: "Uploaded", render: (d) => new Date(d.created_at).toLocaleDateString() },
        ]}
      />

      <Drawer open={open} onClose={() => setOpen(false)} title="Upload Document">
        <form onSubmit={handleUpload}>
          <Field label="Title">
            <TextInput required value={title} onChange={(e) => setTitle(e.target.value)} />
          </Field>
          <Field label="Document Type">
            <Select value={docType} onChange={(e) => setDocType(e.target.value as DocType)}>
              {DOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="File (PDF or text)">
            <input
              type="file"
              required
              accept=".pdf,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm"
            />
          </Field>
          {error && <p className="mb-4 text-sm text-status-poor">{error}</p>}
          <Button type="submit" className="w-full" disabled={uploading}>
            {uploading ? "Uploading & indexing…" : "Upload"}
          </Button>
        </form>
      </Drawer>
    </div>
  );
}
