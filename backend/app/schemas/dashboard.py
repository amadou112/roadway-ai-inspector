from pydantic import BaseModel


class DashboardOverview(BaseModel):
    open_rfis: int
    overdue_rfis: int
    open_submittals: int
    open_risks: int
    high_impact_risks: int
    open_ncrs: int
    open_safety_issues: int
    open_inspection_findings: int
    schedule_on_track: int
    schedule_at_risk: int
    schedule_delayed: int
    budget_total: float
    actual_total: float
    committed_total: float
    variance_total: float


class RiskHeatmapCell(BaseModel):
    likelihood: int
    impact: int
    count: int


class CountByLabel(BaseModel):
    label: str
    count: int
