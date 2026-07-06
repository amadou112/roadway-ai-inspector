"use client";

import { ScheduleItem } from "@/lib/types";
import { EntityCrudPage, InlineSelect } from "@/components/entities/EntityCrudPage";

const endpointBase = (projectId: string) => `/api/v1/projects/${projectId}/schedule-items`;

export default function SchedulePage() {
  return (
    <EntityCrudPage<ScheduleItem>
      title="Schedule"
      description="Construction schedule tasks and progress tracking."
      endpointBase={endpointBase}
      createLabel="+ New Task"
      defaultForm={{ task_name: "", planned_start: "", planned_finish: "", percent_complete: "0" }}
      formFields={[
        { name: "task_name", label: "Task Name", type: "text", required: true },
        { name: "planned_start", label: "Planned Start", type: "date" },
        { name: "planned_finish", label: "Planned Finish", type: "date" },
        { name: "percent_complete", label: "Percent Complete", type: "number" },
      ]}
      columns={({ updateField }) => [
        { header: "Task", render: (s) => <span className="font-medium text-federal-950">{s.task_name}</span> },
        { header: "Planned Start", render: (s) => s.planned_start || "—" },
        { header: "Planned Finish", render: (s) => s.planned_finish || "—" },
        { header: "% Complete", render: (s) => `${s.percent_complete}%` },
        {
          header: "Status",
          render: (s) => (
            <InlineSelect
              value={s.status}
              options={["on_track", "at_risk", "delayed", "complete"]}
              onChange={(v) => updateField(s.id, "status", v)}
            />
          ),
        },
      ]}
    />
  );
}
