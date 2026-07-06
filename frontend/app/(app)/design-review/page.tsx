"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DesignReviewSubmission, DocumentOut } from "@/lib/types";
import { PageHeader, EmptyState } from "@/components/ui/PageHeader";
import { DataTable } from "@/components/ui/DataTable";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { Field, Select } from "@/components/ui/Form";
import { Badge } from "@/components/ui/Badge";

export default function DesignReviewPage() {
  const { selectedProject, loading: projectLoading } = useProject();
  const [submissions, setSubmissions] = useState<DesignReviewSubmission[]>([]);
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [documentId, setDocumentId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function load() {
    if (!selectedProject) return setLoading(false);
    setLoading(true);
    try {
      const [subs, docs] = await Promise.all([
        api.get<DesignReviewSubmission[]>(`/api/v1/projects/${selectedProject.id}/design-reviews`),
        api.get<DocumentOut[]>(`/api/v1/projects/${selectedProject.id}/documents`),
      ]);
      setSubmissions(subs);
      setDocuments(docs);
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
    if (!selectedProject || !documentId) return;
    setSubmitting(true);
    setError(null);
    try {
      const submission = await api.post<DesignReviewSubmission>(
        `/api/v1/projects/${selectedProject.id}/design-reviews`,
        { document_id: documentId }
      );
      setOpen(false);
      router.push(`/design-review/${submission.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to start review");
    } finally {
      setSubmitting(false);
    }
  }

  if (projectLoading || loading) return <p className="text-sm text-slate-400">Loading…</p>;

  if (!selectedProject) {
    return <EmptyState title="No project selected" description="Select a project from the top bar first." />;
  }

  return (
    <div>
      <PageHeader
        title="Design Review Assistant"
        description="AI-powered review of design documents for missing items, conflicts, constructability, safety, and compliance gaps."
        actions={<Button onClick={() => setOpen(true)}>+ New Review</Button>}
      />

      <DataTable<DesignReviewSubmission>
        rows={submissions}
        emptyTitle="No design reviews yet"
        emptyDescription="Upload a plan sheet or design document first, then start a review."
        onRowClick={(s) => router.push(`/design-review/${s.id}`)}
        columns={[
          {
            header: "Document",
            render: (s) => documents.find((d) => d.id === s.document_id)?.title || s.document_id,
          },
          { header: "Reviewed By", render: (s) => s.reviewed_by || "—" },
          { header: "Status", render: (s) => <Badge label={s.status} /> },
          { header: "Findings", render: (s) => s.findings?.length ?? "—" },
          { header: "Date", render: (s) => s.review_date || "—" },
        ]}
      />

      <Drawer open={open} onClose={() => setOpen(false)} title="New Design Review">
        <form onSubmit={handleSubmit}>
          <Field label="Design Document">
            <Select required value={documentId} onChange={(e) => setDocumentId(e.target.value)}>
              <option value="">Select a document…</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title}
                </option>
              ))}
            </Select>
          </Field>
          {documents.length === 0 && (
            <p className="mb-4 text-xs text-slate-400">
              Upload a plan sheet or design document in the Documents tab first.
            </p>
          )}
          {error && <p className="mb-4 text-sm text-status-poor">{error}</p>}
          <Button type="submit" className="w-full" disabled={submitting || !documentId}>
            {submitting ? "Running AI review…" : "Run Review"}
          </Button>
        </form>
      </Drawer>
    </div>
  );
}
