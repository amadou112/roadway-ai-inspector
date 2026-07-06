"use client";

import { Risk } from "@/lib/types";
import { EntityCrudPage, InlineSelect } from "@/components/entities/EntityCrudPage";
import { Badge } from "@/components/ui/Badge";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/risks`;

export default function RisksPage() {
  return (
    <EntityCrudPage<Risk>
      title="Risk Register"
      description="Program and project risks with likelihood × impact scoring."
      endpointBase={endpointBase}
      createLabel="+ New Risk"
      defaultForm={{ title: "", category: "", description: "", likelihood: "3", impact: "3", owner: "", mitigation_plan: "" }}
      formFields={[
        { name: "title", label: "Risk Title", type: "text", required: true },
        { name: "category", label: "Category", type: "text" },
        { name: "description", label: "Description", type: "textarea" },
        {
          name: "likelihood",
          label: "Likelihood (1-5)",
          type: "select",
          options: [1, 2, 3, 4, 5].map((v) => ({ value: String(v), label: String(v) })),
        },
        {
          name: "impact",
          label: "Impact (1-5)",
          type: "select",
          options: [1, 2, 3, 4, 5].map((v) => ({ value: String(v), label: String(v) })),
        },
        { name: "owner", label: "Owner", type: "text" },
        { name: "mitigation_plan", label: "Mitigation Plan", type: "textarea" },
      ]}
      columns={({ updateField }) => [
        { header: "Title", render: (r) => <span className="font-medium text-federal-950">{r.title}</span> },
        { header: "Category", render: (r) => r.category || "—" },
        { header: "L × I", render: (r) => `${r.likelihood} × ${r.impact}` },
        {
          header: "Score",
          render: (r) => <Badge label={r.risk_score >= 16 ? "critical" : r.risk_score >= 9 ? "high" : "low"} />,
        },
        {
          header: "Status",
          render: (r) => (
            <InlineSelect
              value={r.status}
              options={["open", "mitigated", "closed"]}
              onChange={(v) => updateField(r.id, "status", v)}
            />
          ),
        },
        { header: "Owner", render: (r) => r.owner || "—" },
      ]}
    />
  );
}
