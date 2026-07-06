"use client";

import { RFI } from "@/lib/types";
import { EntityCrudPage, InlineSelect } from "@/components/entities/EntityCrudPage";
import { Badge } from "@/components/ui/Badge";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/rfis`;

export default function RFIsPage() {
  return (
    <EntityCrudPage<RFI>
      title="Requests for Information (RFIs)"
      description="Track open questions to the design team and their resolution."
      endpointBase={endpointBase}
      createLabel="+ New RFI"
      defaultForm={{ number: "", subject: "", question: "", priority: "medium", assigned_to: "", due_date: "" }}
      formFields={[
        { name: "number", label: "RFI Number", type: "text", required: true },
        { name: "subject", label: "Subject", type: "text", required: true },
        { name: "question", label: "Question", type: "textarea", required: true },
        {
          name: "priority",
          label: "Priority",
          type: "select",
          options: ["low", "medium", "high", "critical"].map((v) => ({ value: v, label: v })),
        },
        { name: "assigned_to", label: "Assigned To", type: "text" },
        { name: "due_date", label: "Due Date", type: "date" },
      ]}
      columns={({ updateField }) => [
        { header: "#", render: (r) => <span className="font-mono text-xs">{r.number}</span> },
        { header: "Subject", render: (r) => <span className="font-medium text-federal-950">{r.subject}</span> },
        { header: "Priority", render: (r) => <Badge label={r.priority} /> },
        {
          header: "Status",
          render: (r) => (
            <InlineSelect
              value={r.status}
              options={["open", "answered", "closed"]}
              onChange={(v) => updateField(r.id, "status", v)}
            />
          ),
        },
        { header: "Assigned To", render: (r) => r.assigned_to || "—" },
        { header: "Due Date", render: (r) => r.due_date || "—" },
        { header: "Cost Impact", render: (r) => `$${r.cost_impact.toLocaleString()}` },
      ]}
    />
  );
}
