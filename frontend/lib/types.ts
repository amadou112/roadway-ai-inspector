export type Role =
  | "program_manager"
  | "project_manager"
  | "resident_engineer"
  | "inspector"
  | "designer"
  | "contractor"
  | "dot_executive";

export interface UserOut {
  id: string;
  email: string;
  full_name: string;
  role: Role;
}

export interface ProjectOut {
  id: string;
  name: string;
  dot_number: string | null;
  route: string | null;
  county: string | null;
  state: string | null;
  status: string;
  start_date: string | null;
  end_date: string | null;
  budget: number;
  spent: number;
  description: string | null;
  created_at: string;
}

export type DocType =
  | "spec"
  | "fhwa_manual"
  | "inspection_report"
  | "rfi"
  | "submittal"
  | "plan_sheet"
  | "daily_report"
  | "other";

export interface DocumentOut {
  id: string;
  project_id: string;
  title: string;
  doc_type: DocType;
  status: "processing" | "indexed" | "failed";
  page_count: number;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

export interface ChatCitation {
  document_id: string;
  document_title: string;
  page_number: number | null;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  citations: ChatCitation[];
}

export interface RFI {
  id: string;
  project_id: string;
  number: string;
  subject: string;
  question: string;
  status: "open" | "answered" | "closed";
  priority: "low" | "medium" | "high" | "critical";
  submitted_by: string | null;
  assigned_to: string | null;
  submitted_date: string | null;
  due_date: string | null;
  response: string | null;
  cost_impact: number;
  schedule_impact_days: number;
  created_at: string;
}

export interface Submittal {
  id: string;
  project_id: string;
  number: string;
  spec_section: string | null;
  title: string;
  status: "pending" | "under_review" | "approved" | "rejected" | "resubmit_required";
  submitted_date: string | null;
  reviewed_date: string | null;
  reviewer: string | null;
  revision: number;
  notes: string | null;
  created_at: string;
}

export interface Risk {
  id: string;
  project_id: string;
  title: string;
  category: string | null;
  description: string | null;
  likelihood: number;
  impact: number;
  status: "open" | "mitigated" | "closed";
  owner: string | null;
  mitigation_plan: string | null;
  risk_score: number;
  created_at: string;
}

export interface NCR {
  id: string;
  project_id: string;
  ncr_number: string;
  description: string;
  location: string | null;
  spec_reference: string | null;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "corrective_action" | "closed";
  identified_by: string | null;
  identified_date: string | null;
  corrective_action: string | null;
  closed_date: string | null;
  created_at: string;
}

export interface SafetyIssue {
  id: string;
  project_id: string;
  description: string;
  location: string | null;
  severity: "low" | "medium" | "high" | "critical";
  category: "fall_protection" | "equipment" | "traffic_control" | "ppe" | "electrical" | "excavation" | "other";
  status: "open" | "corrective_action" | "closed";
  reported_by: string | null;
  reported_date: string | null;
  corrective_action: string | null;
  created_at: string;
}

export interface ScheduleItem {
  id: string;
  project_id: string;
  task_name: string;
  planned_start: string | null;
  planned_finish: string | null;
  actual_start: string | null;
  actual_finish: string | null;
  percent_complete: number;
  status: "on_track" | "at_risk" | "delayed" | "complete";
  predecessor: string | null;
  created_at: string;
}

export interface CostItem {
  id: string;
  project_id: string;
  category: string;
  budget_amount: number;
  committed_amount: number;
  actual_amount: number;
  change_order_number: string | null;
  variance: number;
  created_at: string;
}

export interface DashboardOverview {
  open_rfis: number;
  overdue_rfis: number;
  open_submittals: number;
  open_risks: number;
  high_impact_risks: number;
  open_ncrs: number;
  open_safety_issues: number;
  open_inspection_findings: number;
  schedule_on_track: number;
  schedule_at_risk: number;
  schedule_delayed: number;
  budget_total: number;
  actual_total: number;
  committed_total: number;
  variance_total: number;
}

export interface DailyInspectionReport {
  id: string;
  project_id: string;
  report_date: string;
  inspector_name: string | null;
  weather_temp_f: number | null;
  weather_conditions: string | null;
  contractor_activities: string[];
  equipment_onsite: string[];
  materials_delivered: Record<string, unknown>[];
  quantities_installed: Record<string, unknown>[];
  deficiencies: Record<string, unknown>[];
  photos: string[];
  narrative: string | null;
  status: "draft" | "submitted";
  created_at: string;
}

export interface DesignReviewFinding {
  id: string;
  category: "missing_item" | "conflict" | "risk" | "constructability" | "safety" | "compliance";
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  sheet_reference: string | null;
  recommendation: string | null;
}

export interface DesignReviewSubmission {
  id: string;
  project_id: string;
  document_id: string;
  reviewed_by: string | null;
  review_date: string | null;
  status: "processing" | "completed" | "failed";
  summary: string | null;
  created_at: string;
  findings: DesignReviewFinding[];
}

export interface Bridge {
  id: string;
  nbi_structure_number: string;
  state: string;
  county: string | null;
  facility_carried: string | null;
  feature_intersected: string | null;
  year_built: number | null;
  adt: number | null;
  latitude: number | null;
  longitude: number | null;
  deck_condition: number | null;
  superstructure_condition: number | null;
  substructure_condition: number | null;
  structural_evaluation: number | null;
  owner: string | null;
  material_type: string | null;
  design_type: string | null;
  condition: "good" | "fair" | "poor" | "unknown";
}

export interface CrashRecord {
  id: string;
  state: string;
  county: string | null;
  case_year: number | null;
  fatalities: number;
  route: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface BridgeDashboardSummary {
  total_bridges: number;
  good_count: number;
  fair_count: number;
  poor_count: number;
  unknown_count: number;
  average_year_built: number | null;
  total_crashes: number;
  total_fatalities: number;
  average_iri: number | null;
  counties: string[];
}

export interface GeneratedReport {
  id: string;
  project_id: string;
  report_type: "weekly_status" | "risk_summary";
  title: string;
  period_start: string | null;
  period_end: string | null;
  generated_by: string | null;
  created_at: string;
}
