"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Bridge, BridgeDashboardSummary, CrashRecord } from "@/lib/types";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, KpiTile } from "@/components/ui/Card";
import { SimpleBarChart } from "@/components/charts/SimpleBarChart";
import { STATUS_COLORS } from "@/lib/chart-colors";

const BridgeMap = dynamic(() => import("@/components/map/BridgeMap"), {
  ssr: false,
  loading: () => <div className="flex h-[420px] items-center justify-center text-sm text-slate-400">Loading map…</div>,
});

export default function BridgesPage() {
  const [summary, setSummary] = useState<BridgeDashboardSummary | null>(null);
  const [bridges, setBridges] = useState<Bridge[]>([]);
  const [crashes, setCrashes] = useState<CrashRecord[]>([]);
  const [county, setCounty] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<BridgeDashboardSummary>("/api/v1/open-data/summary"),
      api.get<CrashRecord[]>("/api/v1/open-data/crashes"),
    ]).then(([s, c]) => {
      setSummary(s);
      setCrashes(c);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    const query = county ? `?county=${encodeURIComponent(county)}` : "";
    api.get<Bridge[]>(`/api/v1/open-data/bridges${query}`).then(setBridges);
  }, [county]);

  const crashesByYear = Object.entries(
    crashes.reduce<Record<string, number>>((acc, c) => {
      const year = String(c.case_year || "Unknown");
      acc[year] = (acc[year] || 0) + 1;
      return acc;
    }, {})
  )
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([label, value]) => ({ label, value, color: STATUS_COLORS.critical }));

  if (loading) return <p className="text-sm text-slate-400">Loading real Delaware DOT open data…</p>;

  return (
    <div>
      <PageHeader
        title="Bridge &amp; Roadway Data Dashboard"
        description="Live National Bridge Inventory (NBI), FARS crash, and pavement condition data for Delaware (FHWA/USDOT open data)."
      />

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiTile label="Total Bridges" value={summary?.total_bridges ?? 0} />
        <KpiTile
          label="Poor Condition"
          value={summary?.poor_count ?? 0}
          tone={summary?.poor_count ? "bad" : "good"}
        />
        <KpiTile label="Avg. Year Built" value={summary?.average_year_built ? Math.round(summary.average_year_built) : "—"} />
        <KpiTile label="Total Crashes Recorded" value={summary?.total_crashes ?? 0} sub={`${summary?.total_fatalities ?? 0} fatalities`} />
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-federal-950">Bridge Locations</h3>
            <select
              className="rounded-md border border-slate-300 px-2 py-1 text-xs"
              value={county}
              onChange={(e) => setCounty(e.target.value)}
            >
              <option value="">All Counties</option>
              {summary?.counties.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <BridgeMap bridges={bridges} />
        </Card>

        <Card>
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Condition Distribution</h3>
          <SimpleBarChart
            data={[
              { label: "Good", value: summary?.good_count ?? 0, color: STATUS_COLORS.good },
              { label: "Fair", value: summary?.fair_count ?? 0, color: STATUS_COLORS.warning },
              { label: "Poor", value: summary?.poor_count ?? 0, color: STATUS_COLORS.critical },
              { label: "Unknown", value: summary?.unknown_count ?? 0, color: STATUS_COLORS.neutral },
            ]}
          />
        </Card>
      </div>

      <Card>
        <h3 className="mb-3 text-sm font-semibold text-federal-950">Crashes by Year (FARS)</h3>
        <SimpleBarChart data={crashesByYear} layout="horizontal" />
      </Card>
    </div>
  );
}
