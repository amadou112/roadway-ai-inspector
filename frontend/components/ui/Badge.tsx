import clsx from "clsx";

const TONE_CLASSES: Record<string, string> = {
  neutral: "bg-slate-100 text-slate-700 border-slate-200",
  blue: "bg-federal-100 text-federal-900 border-federal-500/30",
  green: "bg-green-50 text-green-800 border-green-200",
  amber: "bg-amber-50 text-amber-800 border-amber-200",
  red: "bg-red-50 text-red-700 border-red-200",
};

const STATUS_TONE: Record<string, keyof typeof TONE_CLASSES> = {
  open: "blue",
  pending: "amber",
  under_review: "amber",
  processing: "amber",
  draft: "neutral",
  answered: "green",
  approved: "green",
  completed: "green",
  submitted: "green",
  indexed: "green",
  closed: "neutral",
  mitigated: "green",
  rejected: "red",
  resubmit_required: "red",
  failed: "red",
  corrective_action: "amber",
  on_track: "green",
  at_risk: "amber",
  delayed: "red",
  complete: "green",
  low: "green",
  medium: "amber",
  high: "red",
  critical: "red",
  good: "green",
  fair: "amber",
  poor: "red",
  unknown: "neutral",
};

export function Badge({ label, tone }: { label: string; tone?: keyof typeof TONE_CLASSES }) {
  const resolvedTone = tone || STATUS_TONE[label] || "neutral";
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
        TONE_CLASSES[resolvedTone]
      )}
    >
      {label.replace(/_/g, " ")}
    </span>
  );
}
