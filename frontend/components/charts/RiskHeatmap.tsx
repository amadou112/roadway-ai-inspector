"use client";

import { SEQUENTIAL_BLUE } from "@/lib/chart-colors";

export interface RiskHeatmapCell {
  likelihood: number;
  impact: number;
  count: number;
}

export function RiskHeatmap({ cells }: { cells: RiskHeatmapCell[] }) {
  const maxCount = Math.max(1, ...cells.map((c) => c.count));
  const lookup = new Map(cells.map((c) => [`${c.likelihood}-${c.impact}`, c.count]));

  function colorFor(count: number) {
    if (count === 0) return "#f4f8fc";
    const ratio = count / maxCount;
    const idx = Math.min(SEQUENTIAL_BLUE.length - 1, Math.round(ratio * (SEQUENTIAL_BLUE.length - 1)));
    return SEQUENTIAL_BLUE[idx];
  }

  const levels = [5, 4, 3, 2, 1];

  return (
    <div className="flex gap-2">
      <div className="flex flex-col justify-between py-1 text-[10px] font-semibold uppercase text-slate-400">
        {levels.map((l) => (
          <span key={l} className="flex h-12 items-center">
            {l}
          </span>
        ))}
      </div>
      <div>
        <div className="grid grid-cols-5 gap-1">
          {levels.map((likelihood) =>
            [1, 2, 3, 4, 5].map((impact) => {
              const count = lookup.get(`${likelihood}-${impact}`) || 0;
              return (
                <div
                  key={`${likelihood}-${impact}`}
                  title={`Likelihood ${likelihood} × Impact ${impact}: ${count} risk(s)`}
                  className="flex h-12 w-12 items-center justify-center rounded-md text-xs font-bold text-federal-950"
                  style={{ backgroundColor: colorFor(count) }}
                >
                  {count > 0 ? count : ""}
                </div>
              );
            })
          )}
        </div>
        <p className="mt-2 text-center text-[10px] font-semibold uppercase text-slate-400">Impact →</p>
      </div>
    </div>
  );
}
