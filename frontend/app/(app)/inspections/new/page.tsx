"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useProject } from "@/lib/project-context";
import { DailyInspectionReport } from "@/lib/types";
import { PageHeader, EmptyState } from "@/components/ui/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Field, TextInput, Select } from "@/components/ui/Form";

function ListEditor({
  items,
  setItems,
  placeholder,
}: {
  items: string[];
  setItems: (items: string[]) => void;
  placeholder: string;
}) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={i} className="flex gap-2">
          <TextInput
            value={item}
            placeholder={placeholder}
            onChange={(e) => setItems(items.map((it, idx) => (idx === i ? e.target.value : it)))}
          />
          <button
            type="button"
            onClick={() => setItems(items.filter((_, idx) => idx !== i))}
            className="px-2 text-slate-400 hover:text-status-poor"
          >
            ✕
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => setItems([...items, ""])}
        className="text-xs font-semibold text-federal-700 hover:text-federal-900"
      >
        + Add
      </button>
    </div>
  );
}

interface QtyRow {
  item: string;
  quantity: string;
  unit: string;
}

function QuantityEditor({ rows, setRows }: { rows: QtyRow[]; setRows: (rows: QtyRow[]) => void }) {
  return (
    <div className="space-y-2">
      {rows.map((row, i) => (
        <div key={i} className="flex gap-2">
          <TextInput
            placeholder="Item"
            value={row.item}
            onChange={(e) => setRows(rows.map((r, idx) => (idx === i ? { ...r, item: e.target.value } : r)))}
          />
          <TextInput
            placeholder="Qty"
            className="w-24"
            value={row.quantity}
            onChange={(e) => setRows(rows.map((r, idx) => (idx === i ? { ...r, quantity: e.target.value } : r)))}
          />
          <TextInput
            placeholder="Unit"
            className="w-24"
            value={row.unit}
            onChange={(e) => setRows(rows.map((r, idx) => (idx === i ? { ...r, unit: e.target.value } : r)))}
          />
          <button
            type="button"
            onClick={() => setRows(rows.filter((_, idx) => idx !== i))}
            className="px-2 text-slate-400 hover:text-status-poor"
          >
            ✕
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => setRows([...rows, { item: "", quantity: "", unit: "" }])}
        className="text-xs font-semibold text-federal-700 hover:text-federal-900"
      >
        + Add Item
      </button>
    </div>
  );
}

interface DeficiencyRow {
  description: string;
  severity: string;
  location: string;
}

function DeficiencyEditor({ rows, setRows }: { rows: DeficiencyRow[]; setRows: (rows: DeficiencyRow[]) => void }) {
  return (
    <div className="space-y-2">
      {rows.map((row, i) => (
        <div key={i} className="flex gap-2">
          <TextInput
            placeholder="Description"
            value={row.description}
            onChange={(e) => setRows(rows.map((r, idx) => (idx === i ? { ...r, description: e.target.value } : r)))}
          />
          <Select
            className="w-32"
            value={row.severity}
            onChange={(e) => setRows(rows.map((r, idx) => (idx === i ? { ...r, severity: e.target.value } : r)))}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </Select>
          <TextInput
            placeholder="Location"
            className="w-32"
            value={row.location}
            onChange={(e) => setRows(rows.map((r, idx) => (idx === i ? { ...r, location: e.target.value } : r)))}
          />
          <button
            type="button"
            onClick={() => setRows(rows.filter((_, idx) => idx !== i))}
            className="px-2 text-slate-400 hover:text-status-poor"
          >
            ✕
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => setRows([...rows, { description: "", severity: "low", location: "" }])}
        className="text-xs font-semibold text-federal-700 hover:text-federal-900"
      >
        + Add Deficiency
      </button>
    </div>
  );
}

export default function NewInspectionReportPage() {
  const { selectedProject } = useProject();
  const router = useRouter();
  const [reportDate, setReportDate] = useState(new Date().toISOString().slice(0, 10));
  const [weatherTemp, setWeatherTemp] = useState("");
  const [weatherConditions, setWeatherConditions] = useState("");
  const [contractorActivities, setContractorActivities] = useState<string[]>([""]);
  const [equipmentOnsite, setEquipmentOnsite] = useState<string[]>([""]);
  const [materials, setMaterials] = useState<QtyRow[]>([{ item: "", quantity: "", unit: "" }]);
  const [quantities, setQuantities] = useState<QtyRow[]>([{ item: "", quantity: "", unit: "" }]);
  const [deficiencies, setDeficiencies] = useState<DeficiencyRow[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!selectedProject) {
    return <EmptyState title="No project selected" description="Select a project from the top bar first." />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const report = await api.post<DailyInspectionReport>(
        `/api/v1/projects/${selectedProject!.id}/inspection-reports`,
        {
          report_date: reportDate,
          weather_temp_f: weatherTemp ? Number(weatherTemp) : null,
          weather_conditions: weatherConditions,
          contractor_activities: contractorActivities.filter(Boolean),
          equipment_onsite: equipmentOnsite.filter(Boolean),
          materials_delivered: materials.filter((m) => m.item),
          quantities_installed: quantities.filter((q) => q.item),
          deficiencies: deficiencies.filter((d) => d.description),
          photos: [],
        }
      );
      router.push(`/inspections/${report.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to generate report");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader title="New Daily Inspection Report" description="Enter field data — AI will generate the narrative report." />

      <form onSubmit={handleSubmit}>
        <Card className="mb-4">
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Date &amp; Weather</h3>
          <div className="grid grid-cols-3 gap-3">
            <Field label="Report Date">
              <TextInput type="date" required value={reportDate} onChange={(e) => setReportDate(e.target.value)} />
            </Field>
            <Field label="Temp (°F)">
              <TextInput type="number" value={weatherTemp} onChange={(e) => setWeatherTemp(e.target.value)} />
            </Field>
            <Field label="Conditions">
              <TextInput
                placeholder="Sunny, clear"
                value={weatherConditions}
                onChange={(e) => setWeatherConditions(e.target.value)}
              />
            </Field>
          </div>
        </Card>

        <Card className="mb-4">
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Contractor Activities</h3>
          <ListEditor items={contractorActivities} setItems={setContractorActivities} placeholder="e.g. Placed concrete deck pour, Station 12+00 to 14+50" />
        </Card>

        <Card className="mb-4">
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Equipment Onsite</h3>
          <ListEditor items={equipmentOnsite} setItems={setEquipmentOnsite} placeholder="e.g. Concrete pump truck" />
        </Card>

        <Card className="mb-4">
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Materials Delivered</h3>
          <QuantityEditor rows={materials} setRows={setMaterials} />
        </Card>

        <Card className="mb-4">
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Quantities Installed</h3>
          <QuantityEditor rows={quantities} setRows={setQuantities} />
        </Card>

        <Card className="mb-4">
          <h3 className="mb-3 text-sm font-semibold text-federal-950">Deficiencies</h3>
          <DeficiencyEditor rows={deficiencies} setRows={setDeficiencies} />
        </Card>

        {error && <p className="mb-4 text-sm text-status-poor">{error}</p>}
        <Button type="submit" disabled={submitting} className="w-full">
          {submitting ? "Generating report with AI…" : "Generate Inspection Report"}
        </Button>
      </form>
    </div>
  );
}
