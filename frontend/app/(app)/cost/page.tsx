"use client";

import { CostItem } from "@/lib/types";
import { EntityCrudPage } from "@/components/entities/EntityCrudPage";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/cost-items`;

export default function CostPage() {
  return (
    <EntityCrudPage<CostItem>
      title="Cost Tracking"
      description="Budget, committed, and actual costs by category."
      endpointBase={endpointBase}
      createLabel="+ New Cost Item"
      defaultForm={{ category: "", budget_amount: "", committed_amount: "", actual_amount: "" }}
      formFields={[
        { name: "category", label: "Category", type: "text", required: true },
        { name: "budget_amount", label: "Budget Amount (USD)", type: "number" },
        { name: "committed_amount", label: "Committed Amount (USD)", type: "number" },
        { name: "actual_amount", label: "Actual Amount (USD)", type: "number" },
      ]}
      columns={[
        { header: "Category", render: (c) => <span className="font-medium text-federal-950">{c.category}</span> },
        { header: "Budget", render: (c) => `$${c.budget_amount.toLocaleString()}` },
        { header: "Committed", render: (c) => `$${c.committed_amount.toLocaleString()}` },
        { header: "Actual", render: (c) => `$${c.actual_amount.toLocaleString()}` },
        {
          header: "Variance",
          render: (c) => (
            <span className={c.variance < 0 ? "font-semibold text-status-poor" : "font-semibold text-status-good"}>
              ${c.variance.toLocaleString()}
            </span>
          ),
        },
      ]}
    />
  );
}
