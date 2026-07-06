"use client";

import { NCR } from "@/lib/types";
import { EntityCrudPage, InlineSelect } from "@/components/entities/EntityCrudPage";
import { Badge } from "@/components/ui/Badge";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/ncrs`;

export default function NCRsPage() {
  return (
    <EntityCrudPage<NCR>
      title="Non-Conformance Reports"
      description="Deviations from specifications and their corrective actions."
      endpointBase={endpointBase}
      createLabel="+ New NCR"
      defaultForm={{
        ncr_number: "",
        description: "",
        location: "",
        spec_reference: "",
        severity: "medium",
        identified_by: "",
        identified_date: "",
      }}
      formFields={[
        { name: "ncr_number", label: "NCR Number", type: "text", required: true },
        { name: "description", label: "Description", type: "textarea", required: true },
        { name: "location", label: "Location", type: "text" },
        { name: "spec_reference", label: "Spec Reference", type: "text" },
        {
          name: "severity",
          label: "Severity",
          type: "select",
          options: ["low", "medium", "high", "critical"].map((v) => ({ value: v, label: v })),
        },
        { name: "identified_by", label: "Identified By", type: "text" },
        { name: "identified_date", label: "Identified Date", type: "date" },
      ]}
      columns={({ updateField }) => [
        { header: "#", render: (n) => <span className="font-mono text-xs">{n.ncr_number}</span> },
        { header: "Description", render: (n) => <span className="font-medium text-federal-950">{n.description}</span> },
        { header: "Severity", render: (n) => <Badge label={n.severity} /> },
        {
          header: "Status",
          render: (n) => (
            <InlineSelect
              value={n.status}
              options={["open", "corrective_action", "closed"]}
              onChange={(v) => updateField(n.id, "status", v)}
            />
          ),
        },
        { header: "Location", render: (n) => n.location || "—" },
        { header: "Identified", render: (n) => n.identified_date || "—" },
      ]}
    />
  );
}
