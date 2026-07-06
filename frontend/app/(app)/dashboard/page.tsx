"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DashboardOverview } from "@/lib/types";
import { PageHeader, EmptyState } from "@/components/ui/PageHeader";
import { Card, KpiTile } from "@/components/ui/Card";
import { RiskHeatmap, RiskHeatmapCell } from "@/components/charts/RiskHeatmap";
import { SimpleBarChart } from "@/components/charts/SimpleBarChart";
import { TrendLineChart } from "@/components/charts/TrendLineChart";
import { CATEGORICAL, STATUS_COLORS } from "@/lib/chart-colors";

interface CountByLabel {
  label: string;
  count: number;
}

export default function DashboardPage() {
  const { selectedProject, loading: projectLoading } = useProject();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [heatmap, setHeatmap] = useState<RiskHeatmapCell[]>([]);
  const [safetyByCategory, setSafetyByCategory] = useState<CountByLabel[]>([]);
  const [ncrTrend, setNcrTrend] = useState<CountByLabel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedProject) {
      setLoading(false);
      return;
    }
    setLoading(true);
    const base = `/api/v1/projects/${selectedProject.id}/dashboard`;
    Promise.all([
      api.get<DashboardOverview>(`${base}/overview`),
      api.get<RiskHeatmapCell[]>(`${base}/risk-heatmap`),
      api.get<CountByLabel[]>(`${base}/safety-by-category`),
      api.get<CountByLabel[]>(`${base}/ncr-trend`),
    ])
      .then(([ov, hm, safety, ncr]) => {
        setOverview(ov);
        setHeatmap(hm);
        setSafetyByCategory(safety);
        setNcrTrend(ncr);
      })
      .finally(() => setLoading(false));
  }, [selectedProject]);

  if (projectLoading || loading) {
    return <p className="text-sm text-slate-400">Loading dashboard…</p>;
  }

  if (!selectedProject) {
    return (
      <EmptyState
        title="No project selected"
        description="Create or select a project from the Projects tab to see its dashboard."
      />
    );
  }

  return (
    <div>
      <PageHeader
        title="Program Dashboard"
        description={`${selectedProject.name} — ${selectedProject.route || ""} ${selectedProject.county ? `· ${selectedProject.county} County` : ""}`}
      />

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <KpiTile label="Open RFIs" value={overview?.open_rfis ?? 0} tone={overview?.overdue_rfis ? "bad" : "neutral"} sub={overview?.overdue_rfis ? `${overview.overdue_rfis} overdue` : undefined} />
        <KpiTile label="Open Submittals" value={overview?.open_submittals ?? 0} />
        <KpiTile label="Open Risks" value={overview?.open_risks ?? 0} tone={overview?.high_impact_risks ? "bad" : "neutral"} sub={overview?.high_impact_risks ? `${overview.high_impact_risks} high-impact` : undefined} />
        <KpiTile label="Open NCRs" value={overview?.open_ncrs ?? 0} tone={overview?.open_ncrs ? "warn" : "good"} />
        <KpiTile label="Open Safety Issues" value={overview?.open_safety_issues ?? 0} tone={overview?.open_safety_issues ? "warn" : "good"} />
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <KpiTile label="Budget" value={`$${(overview?.budget_total ?? 0).toLocaleString()}`} />
        <KpiTile label="Actual Spend" value={`$${(overview?.actual_total ?? 0).toLocaleString()}`} />
        <KpiTile
          label="Variance"
          value={`$${(overview?.variance_total ?? 0).toLocaleString()}`}
          tone={(overview?.variance_total ?? 0) < 0 ? "bad" : "good"}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Schedule Status</h3>
          <SimpleBarChart
            data={[
              { label: "On Track", value: overview?.schedule_on_track ?? 0, color: STATUS_COLORS.good },
              { label: "At Risk", value: overview?.schedule_at_risk ?? 0, color: STATUS_COLORS.warning },
              { label: "Delayed", value: overview?.schedule_delayed ?? 0, color: STATUS_COLORS.critical },
            ]}
          />
        </Card>

        <Card>
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Risk Heat Map (Likelihood × Impact)</h3>
          {heatmap.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">No open risks recorded.</p>
          ) : (
            <RiskHeatmap cells={heatmap} />
          )}
        </Card>

        <Card>
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Safety Issues by Category</h3>
          <SimpleBarChart
            data={safetyByCategory.map((d, i) => ({
              label: d.label.replace(/_/g, " "),
              value: d.count,
              color: CATEGORICAL[i % CATEGORICAL.length],
            }))}
          />
        </Card>

        <Card>
          <h3 className="mb-3 text-sm font-semibold text-federal-950">NCR Trend</h3>
          <TrendLineChart data={ncrTrend.map((d) => ({ label: d.label, value: d.count }))} />
        </Card>
      </div>
    </div>
  );
}
