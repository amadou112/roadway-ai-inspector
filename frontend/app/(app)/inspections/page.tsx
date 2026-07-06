"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DailyInspectionReport } from "@/lib/types";
import { PageHeader, EmptyState } from "@/components/ui/PageHeader";
import { DataTable } from "@/components/ui/DataTable";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export default function InspectionsPage() {
  const { selectedProject, loading: projectLoading } = useProject();
  const [reports, setReports] = useState<DailyInspectionReport[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!selectedProject) return setLoading(false);
    setLoading(true);
    api
      .get<DailyInspectionReport[]>(`/api/v1/projects/${selectedProject.id}/inspection-reports`)
      .then(setReports)
      .finally(() => setLoading(false));
  }, [selectedProject]);

  if (projectLoading || loading) return <p className="text-sm text-slate-400">Loading…</p>;

  if (!selectedProject) {
    return <EmptyState title="No project selected" description="Select a project from the top bar first." />;
  }

  return (
    <div>
      <PageHeader
        title="Daily Inspection Reports"
        description="AI-generated daily inspection reports from field notes, quantities, weather, and deficiencies."
        actions={<Button onClick={() => router.push("/inspections/new")}>+ New Inspection Report</Button>}
      />

      <DataTable<DailyInspectionReport>
        rows={reports}
        emptyTitle="No inspection reports yet"
        emptyDescription="Create your first daily inspection report."
        onRowClick={(r) => router.push(`/inspections/${r.id}`)}
        columns={[
          { header: "Date", render: (r) => r.report_date },
          { header: "Inspector", render: (r) => r.inspector_name || "—" },
          { header: "Weather", render: (r) => r.weather_conditions || "—" },
          { header: "Deficiencies", render: (r) => r.deficiencies.length },
          { header: "Status", render: (r) => <Badge label={r.status} /> },
        ]}
      />
    </div>
  );
}
