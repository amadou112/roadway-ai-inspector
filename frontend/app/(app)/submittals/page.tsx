"use client";

import { Submittal } from "@/lib/types";
import { EntityCrudPage, InlineSelect } from "@/components/entities/EntityCrudPage";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/submittals`;

export default function SubmittalsPage() {
  return (
    <EntityCrudPage<Submittal>
      title="Submittals"
      description="Contractor submittals under DOT/design review."
      endpointBase={endpointBase}
      createLabel="+ New Submittal"
      defaultForm={{ number: "", spec_section: "", title: "", reviewer: "" }}
      formFields={[
        { name: "number", label: "Submittal Number", type: "text", required: true },
        { name: "spec_section", label: "Spec Section", type: "text" },
        { name: "title", label: "Title", type: "text", required: true },
        { name: "reviewer", label: "Reviewer", type: "text" },
      ]}
      columns={({ updateField }) => [
        { header: "#", render: (s) => <span className="font-mono text-xs">{s.number}</span> },
        { header: "Title", render: (s) => <span className="font-medium text-federal-950">{s.title}</span> },
        { header: "Spec Section", render: (s) => s.spec_section || "—" },
        {
          header: "Status",
          render: (s) => (
            <InlineSelect
              value={s.status}
              options={["pending", "under_review", "approved", "rejected", "resubmit_required"]}
              onChange={(v) => updateField(s.id, "status", v)}
            />
          ),
        },
        { header: "Reviewer", render: (s) => s.reviewer || "—" },
        { header: "Revision", render: (s) => s.revision },
      ]}
    />
  );
}
