"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DailyInspectionReport } from "@/lib/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export function InspectionDetailClient({ reportId }: { reportId: string }) {
  const { selectedProject } = useProject();
  const [report, setReport] = useState<DailyInspectionReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedProject) return;
    api
      .get<DailyInspectionReport>(`/api/v1/projects/${selectedProject.id}/inspection-reports/${reportId}`)
      .then(setReport)
      .finally(() => setLoading(false));
  }, [selectedProject, reportId]);

  if (loading) return <p className="text-sm text-slate-400">Loading…</p>;
  if (!report || !selectedProject) return <p className="text-sm text-slate-400">Report not found.</p>;

  const pdfUrl = api.fileUrl(
    `/api/v1/projects/${selectedProject.id}/inspection-reports/${report.id}/pdf`
  );

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title={`Daily Inspection Report — ${report.report_date}`}
        description={`Inspector: ${report.inspector_name || "—"}`}
        actions={
          <a href={pdfUrl} target="_blank" rel="noreferrer">
            <Button variant="secondary">⬇ Download PDF</Button>
          </a>
        }
      />

      <Card className="mb-4">
        <div className="mb-2 flex items-center gap-2">
          <Badge label={report.status} />
          <span className="text-sm text-slate-500">
            {report.weather_conditions} {report.weather_temp_f ? `· ${report.weather_temp_f}°F` : ""}
          </span>
        </div>
        <div className="whitespace-pre-wrap text-sm leading-relaxed text-federal-950">{report.narrative}</div>
      </Card>

      {report.deficiencies.length > 0 && (
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Deficiencies</h3>
          <ul className="space-y-2 text-sm">
            {report.deficiencies.map((d, i) => (
              <li key={i} className="flex items-center gap-2">
                <Badge label={String(d.severity || "medium")} />
                <span>{String(d.description)}</span>
                {d.location ? <span className="text-slate-400">— {String(d.location)}</span> : null}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
