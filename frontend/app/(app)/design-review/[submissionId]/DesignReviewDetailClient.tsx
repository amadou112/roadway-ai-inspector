"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DesignReviewSubmission } from "@/lib/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export function DesignReviewDetailClient({ submissionId }: { submissionId: string }) {
  const { selectedProject } = useProject();
  const [submission, setSubmission] = useState<DesignReviewSubmission | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedProject) return;
    api
      .get<DesignReviewSubmission>(`/api/v1/projects/${selectedProject.id}/design-reviews/${submissionId}`)
      .then(setSubmission)
      .finally(() => setLoading(false));
  }, [selectedProject, submissionId]);

  if (loading) return <p className="text-sm text-slate-400">Loading…</p>;
  if (!submission || !selectedProject) return <p className="text-sm text-slate-400">Review not found.</p>;

  const pdfUrl = api.fileUrl(
    `/api/v1/projects/${selectedProject.id}/design-reviews/${submission.id}/pdf`
  );

  const grouped = submission.findings.reduce<Record<string, typeof submission.findings>>((acc, f) => {
    (acc[f.category] ||= []).push(f);
    return acc;
  }, {});

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title="Design Review Findings"
        description={submission.summary || ""}
        actions={
          submission.status === "completed" ? (
            <a href={pdfUrl} target="_blank" rel="noreferrer">
              <Button variant="secondary">⬇ Download PDF</Button>
            </a>
          ) : undefined
        }
      />

      <Card className="mb-4 flex items-center gap-2">
        <Badge label={submission.status} />
        <span className="text-sm text-slate-500">Reviewed by {submission.reviewed_by}</span>
      </Card>

      {Object.entries(grouped).map(([category, findings]) => (
        <Card key={category} className="mb-4">
          <h3 className="mb-3 text-sm font-semibold capitalize text-federal-950">{category.replace(/_/g, " ")}</h3>
          <ul className="space-y-3">
            {findings.map((f) => (
              <li key={f.id} className="border-b border-slate-100 pb-3 last:border-0 last:pb-0">
                <div className="mb-1 flex items-center gap-2">
                  <Badge label={f.severity} />
                  {f.sheet_reference && <span className="text-xs text-slate-400">Sheet: {f.sheet_reference}</span>}
                </div>
                <p className="text-sm text-federal-950">{f.description}</p>
                {f.recommendation && <p className="mt-1 text-xs text-slate-500">Recommendation: {f.recommendation}</p>}
              </li>
            ))}
          </ul>
        </Card>
      ))}
    </div>
  );
}
