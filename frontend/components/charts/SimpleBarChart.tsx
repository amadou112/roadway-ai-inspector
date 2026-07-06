"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CHART_AXIS, CHART_GRID } from "@/lib/chart-colors";

export interface BarDatum {
  label: string;
  value: number;
  color: string;
}

export function SimpleBarChart({ data, height = 240, layout = "vertical" }: { data: BarDatum[]; height?: number; layout?: "vertical" | "horizontal" }) {
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-slate-400">No data yet.</p>;
  }

  const isHorizontalBars = layout === "vertical"; // bars drawn horizontally, category on Y

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={isHorizontalBars ? "vertical" : "horizontal"}
        margin={{ top: 4, right: 16, bottom: 4, left: isHorizontalBars ? 24 : 0 }}
      >
        <CartesianGrid stroke={CHART_GRID} horizontal={!isHorizontalBars} vertical={isHorizontalBars} />
        {isHorizontalBars ? (
          <>
            <XAxis type="number" tick={{ fontSize: 11, fill: CHART_AXIS }} allowDecimals={false} />
            <YAxis type="category" dataKey="label" tick={{ fontSize: 11, fill: CHART_AXIS }} width={130} />
          </>
        ) : (
          <>
            <XAxis type="category" dataKey="label" tick={{ fontSize: 11, fill: CHART_AXIS }} />
            <YAxis type="number" tick={{ fontSize: 11, fill: CHART_AXIS }} allowDecimals={false} />
          </>
        )}
        <Tooltip
          cursor={{ fill: "rgba(11,61,98,0.06)" }}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #dde5ee" }}
        />
        <Bar dataKey="value" radius={4} maxBarSize={28}>
          {data.map((d, i) => (
            <Cell key={i} fill={d.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
