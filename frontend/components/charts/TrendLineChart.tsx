"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_AXIS, CHART_GRID, SEQUENTIAL_BLUE } from "@/lib/chart-colors";

export function TrendLineChart({
  data,
  height = 240,
}: {
  data: { label: string; value: number }[];
  height?: number;
}) {
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-slate-400">No data yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
        <CartesianGrid stroke={CHART_GRID} vertical={false} />
        <XAxis dataKey="label" tick={{ fontSize: 11, fill: CHART_AXIS }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: CHART_AXIS }} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #dde5ee" }} />
        <Line
          type="monotone"
          dataKey="value"
          stroke={SEQUENTIAL_BLUE[4]}
          strokeWidth={2}
          dot={{ r: 3, fill: SEQUENTIAL_BLUE[4] }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
