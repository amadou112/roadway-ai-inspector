"use client";

import { SafetyIssue } from "@/lib/types";
import { EntityCrudPage, InlineSelect } from "@/components/entities/EntityCrudPage";
import { Badge } from "@/components/ui/Badge";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/safety-issues`;

export default function SafetyPage() {
  return (
    <EntityCrudPage<SafetyIssue>
      title="Safety Issues"
      description="Field safety observations, hazards, and corrective actions."
      endpointBase={endpointBase}
      createLabel="+ New Safety Issue"
      defaultForm={{ description: "", location: "", severity: "medium", category: "other", reported_by: "", reported_date: "" }}
      formFields={[
        { name: "description", label: "Description", type: "textarea", required: true },
        { name: "location", label: "Location", type: "text" },
        {
          name: "severity",
          label: "Severity",
          type: "select",
          options: ["low", "medium", "high", "critical"].map((v) => ({ value: v, label: v })),
        },
        {
          name: "category",
          label: "Category",
          type: "select",
          options: ["fall_protection", "equipment", "traffic_control", "ppe", "electrical", "excavation", "other"].map(
            (v) => ({ value: v, label: v.replace(/_/g, " ") })
          ),
        },
        { name: "reported_by", label: "Reported By", type: "text" },
        { name: "reported_date", label: "Reported Date", type: "date" },
      ]}
      columns={({ updateField }) => [
        { header: "Description", render: (s) => <span className="font-medium text-federal-950">{s.description}</span> },
        { header: "Category", render: (s) => <Badge label={s.category} tone="blue" /> },
        { header: "Severity", render: (s) => <Badge label={s.severity} /> },
        {
          header: "Status",
          render: (s) => (
            <InlineSelect
              value={s.status}
              options={["open", "corrective_action", "closed"]}
              onChange={(v) => updateField(s.id, "status", v)}
            />
          ),
        },
        { header: "Location", render: (s) => s.location || "—" },
      ]}
    />
  );
}
