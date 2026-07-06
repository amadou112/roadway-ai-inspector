"""Seeds one demo project ("I-95 Corridor Improvement — Delaware") with
representative RFIs, submittals, risks, NCRs, safety issues, schedule items,
cost items, and two sample specification documents (indexed into the RAG
vector store) so every feature has something to demo on first run.

Safe to re-run: skips seeding if the demo project already exists.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.enums import DocTypeEnum
from app.models.pm import RFI, CostItem, NonConformanceReport, Risk, SafetyIssue, ScheduleItem, Submittal
from app.models.project import Project
from app.services import ingestion

settings = get_settings()
DEMO_PROJECT_NAME = "I-95 Corridor Improvement — Delaware"
TODAY = date.today()

SAMPLE_DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_spec_excerpts"


def seed_project(db) -> Project:
    project = Project(
        name=DEMO_PROJECT_NAME,
        dot_number="DELDOT-2026-0113",
        route="I-95",
        county="New Castle",
        state="DE",
        status="active",
        start_date=TODAY - timedelta(days=200),
        end_date=TODAY + timedelta(days=650),
        budget=48_500_000,
        spent=15_200_000,
        description=(
            "Widening and bridge deck replacement along I-95 through New Castle County, "
            "including drainage upgrades, MOT phasing, and full-depth pavement reconstruction."
        ),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def seed_rfis(db, project_id):
    rows = [
        dict(
            number="RFI-001",
            subject="Drainage pipe conflict at Station 145+00",
            question="Existing gas utility conflicts with proposed 36-in RCP storm drain alignment. Please advise on relocation vs. realignment.",
            status="open",
            priority="high",
            submitted_by="Contractor",
            assigned_to="Design Team",
            submitted_date=TODAY - timedelta(days=10),
            due_date=TODAY + timedelta(days=4),
            cost_impact=18500,
            schedule_impact_days=5,
        ),
        dict(
            number="RFI-002",
            subject="Concrete mix design clarification",
            question="Section 812.03 requires 4,500 psi for bridge deck. Confirm applicability to approach slabs.",
            status="answered",
            priority="medium",
            submitted_by="Contractor",
            assigned_to="Resident Engineer",
            submitted_date=TODAY - timedelta(days=30),
            due_date=TODAY - timedelta(days=16),
            response="Approach slabs shall use Class A (4,500 psi) concrete, consistent with bridge deck requirements.",
        ),
        dict(
            number="RFI-003",
            subject="MOT phasing for bridge deck pour",
            question="Requesting confirmation of lane closure window for continuous deck pour on Bridge 1-234.",
            status="open",
            priority="high",
            submitted_by="Contractor",
            assigned_to="Resident Engineer",
            submitted_date=TODAY - timedelta(days=5),
            due_date=TODAY + timedelta(days=9),
        ),
        dict(
            number="RFI-004",
            subject="Guardrail end treatment type",
            question="Plans reference two possible end treatment types at Station 210+50; please clarify which governs.",
            status="closed",
            priority="low",
            submitted_by="Contractor",
            assigned_to="Design Team",
            submitted_date=TODAY - timedelta(days=60),
            due_date=TODAY - timedelta(days=46),
            response="Type III MELT end treatment governs per Detail 12 on Sheet 47.",
        ),
        dict(
            number="RFI-005",
            subject="Utility relocation coordination — fiber optic",
            question="Fiber optic conduit shown on utility plans conflicts with proposed retaining wall footing.",
            status="open",
            priority="critical",
            submitted_by="Contractor",
            assigned_to="Program Manager",
            submitted_date=TODAY - timedelta(days=3),
            due_date=TODAY + timedelta(days=11),
            cost_impact=42000,
            schedule_impact_days=10,
        ),
    ]
    for r in rows:
        db.add(RFI(project_id=project_id, **r))


def seed_submittals(db, project_id):
    rows = [
        dict(number="SUB-001", spec_section="812", title="Bridge Deck Concrete Mix Design", status="approved",
             submitted_date=TODAY - timedelta(days=45), reviewed_date=TODAY - timedelta(days=35), reviewer="Resident Engineer", revision=1),
        dict(number="SUB-002", spec_section="709", title="Reinforcing Steel Shop Drawings", status="under_review",
             submitted_date=TODAY - timedelta(days=8), reviewer="Resident Engineer", revision=0),
        dict(number="SUB-003", spec_section="606", title="Guardrail Product Data", status="approved",
             submitted_date=TODAY - timedelta(days=50), reviewed_date=TODAY - timedelta(days=42), reviewer="Design Team", revision=0),
        dict(number="SUB-004", spec_section="632", title="Traffic Signal Equipment Submittal", status="resubmit_required",
             submitted_date=TODAY - timedelta(days=20), reviewed_date=TODAY - timedelta(days=12), reviewer="Resident Engineer",
             notes="Conduit fill calculations missing; resubmit with complete conduit schedule.", revision=1),
        dict(number="SUB-005", spec_section="212", title="Erosion & Sediment Control Plan", status="pending",
             submitted_date=TODAY - timedelta(days=2), revision=0),
    ]
    for r in rows:
        db.add(Submittal(project_id=project_id, **r))


def seed_risks(db, project_id):
    rows = [
        dict(title="Extended winter weather delays", category="Weather", description="Above-average snowfall could delay earthwork and paving operations.",
             likelihood=4, impact=3, status="open", owner="Project Manager", mitigation_plan="Maintain 15-day float in winter months; pre-stage cold-weather concreting plan."),
        dict(title="Unresolved utility conflicts", category="Utilities", description="Multiple utility conflicts identified in drainage design not yet resolved.",
             likelihood=4, impact=4, status="open", owner="Resident Engineer", mitigation_plan="Weekly utility coordination meetings; escalate unresolved conflicts within 5 days."),
        dict(title="Structural steel price escalation", category="Cost", description="Steel price volatility could impact bridge superstructure costs.",
             likelihood=3, impact=4, status="open", owner="Program Manager", mitigation_plan="Lock pricing via early material procurement where contract allows."),
        dict(title="Subcontractor default — paving subcontractor", category="Contractor", description="Paving subcontractor has shown signs of financial distress on other projects.",
             likelihood=2, impact=5, status="open", owner="Program Manager", mitigation_plan="Monitor payment bond status; identify backup paving subcontractor."),
        dict(title="Right-of-way acquisition delay", category="ROW", description="Two remaining parcels not yet acquired near Station 190+00.",
             likelihood=3, impact=3, status="mitigated", owner="Program Manager", mitigation_plan="Legal counsel engaged; acquisition expected to close within 30 days."),
        dict(title="Hazardous material discovery during excavation", category="Environmental", description="Potential for legacy contamination near former fueling station adjacent to ROW.",
             likelihood=2, impact=4, status="open", owner="Resident Engineer", mitigation_plan="Pre-excavation soil sampling scheduled; contingency disposal plan on file."),
    ]
    for r in rows:
        db.add(Risk(project_id=project_id, **r))


def seed_ncrs(db, project_id):
    rows = [
        dict(ncr_number="NCR-001", description="Reinforcing steel cover deficient on bridge deck top mat, measured 1.8 in vs 2.5 in required.",
             location="Bridge 1-234, Deck Panel 3", spec_reference="812.06", severity="high", status="corrective_action",
             identified_by="Inspector", identified_date=TODAY - timedelta(days=14), corrective_action="Additional chairs installed to raise mat; re-inspected and accepted."),
        dict(ncr_number="NCR-002", description="Concrete cylinder break at 89% of specified 28-day strength.",
             location="Substructure Pier 2", spec_reference="812.07", severity="medium", status="closed",
             identified_by="Resident Engineer", identified_date=TODAY - timedelta(days=40), corrective_action="Core samples taken; in-place strength confirmed acceptable per ACI 318 core evaluation.",
             closed_date=TODAY - timedelta(days=25)),
        dict(ncr_number="NCR-003", description="Field weld on guardrail post shows undercut exceeding AWS D1.1 tolerance.",
             location="Station 208+00", spec_reference="606.09", severity="medium", status="open",
             identified_by="Inspector", identified_date=TODAY - timedelta(days=3)),
        dict(ncr_number="NCR-004", description="Subgrade compaction test failed at 92% vs 95% required, Station 160+00 to 162+00.",
             location="Roadway Station 160+00", spec_reference="204.03", severity="low", status="closed",
             identified_by="Inspector", identified_date=TODAY - timedelta(days=55), corrective_action="Recompacted and retested; passed at 96%.",
             closed_date=TODAY - timedelta(days=52)),
    ]
    for r in rows:
        db.add(NonConformanceReport(project_id=project_id, **r))


def seed_safety(db, project_id):
    rows = [
        dict(description="Worker observed on bridge deck edge without fall protection harness attached.",
             location="Bridge 1-234", severity="critical", category="fall_protection", status="closed",
             reported_by="Inspector", reported_date=TODAY - timedelta(days=18), corrective_action="Work stopped; toolbox talk conducted; harness use enforced with daily spot checks."),
        dict(description="Excavation shoring not extended full depth at utility trench.",
             location="Station 145+00", severity="high", category="excavation", status="corrective_action",
             reported_by="Resident Engineer", reported_date=TODAY - timedelta(days=6)),
        dict(description="Flagger positioned outside designated MOT taper, reduced visibility to approaching traffic.",
             location="Station 190+00", severity="medium", category="traffic_control", status="closed",
             reported_by="Inspector", reported_date=TODAY - timedelta(days=22), corrective_action="MOT layout adjusted per approved plan; flagger repositioned."),
        dict(description="Two laborers observed without hearing protection near concrete saw operation.",
             location="Station 205+00", severity="low", category="ppe", status="closed",
             reported_by="Inspector", reported_date=TODAY - timedelta(days=35), corrective_action="PPE reissued; toolbox talk conducted."),
        dict(description="Crane annual inspection certificate expired, still in active use.",
             location="Bridge 1-234 laydown yard", severity="high", category="equipment", status="open",
             reported_by="Resident Engineer", reported_date=TODAY - timedelta(days=1)),
    ]
    for r in rows:
        db.add(SafetyIssue(project_id=project_id, **r))


def seed_schedule(db, project_id):
    start = TODAY - timedelta(days=200)
    rows = [
        dict(task_name="Mobilization & MOT Setup", planned_start=start, planned_finish=start + timedelta(days=20),
             actual_start=start, actual_finish=start + timedelta(days=18), percent_complete=100, status="complete"),
        dict(task_name="Demolition — Existing Bridge Deck", planned_start=start + timedelta(days=20), planned_finish=start + timedelta(days=50),
             actual_start=start + timedelta(days=22), actual_finish=start + timedelta(days=55), percent_complete=100, status="complete"),
        dict(task_name="Roadway Earthwork", planned_start=start + timedelta(days=40), planned_finish=start + timedelta(days=110),
             actual_start=start + timedelta(days=45), percent_complete=90, status="on_track"),
        dict(task_name="Storm Drain Installation", planned_start=start + timedelta(days=60), planned_finish=start + timedelta(days=130),
             actual_start=start + timedelta(days=68), percent_complete=65, status="at_risk"),
        dict(task_name="Bridge Substructure Construction", planned_start=start + timedelta(days=70), planned_finish=start + timedelta(days=170),
             actual_start=start + timedelta(days=75), percent_complete=55, status="on_track"),
        dict(task_name="Bridge Superstructure & Deck Pour", planned_start=start + timedelta(days=170), planned_finish=start + timedelta(days=260),
             percent_complete=10, status="at_risk"),
        dict(task_name="Full-Depth Pavement Reconstruction", planned_start=start + timedelta(days=260), planned_finish=start + timedelta(days=380),
             percent_complete=0, status="on_track"),
        dict(task_name="Final Paving, Striping & Signage", planned_start=start + timedelta(days=380), planned_finish=start + timedelta(days=420),
             percent_complete=0, status="on_track"),
    ]
    for r in rows:
        db.add(ScheduleItem(project_id=project_id, **r))


def seed_cost(db, project_id):
    rows = [
        dict(category="Mobilization", budget_amount=1_200_000, committed_amount=1_200_000, actual_amount=1_180_000),
        dict(category="Earthwork", budget_amount=6_500_000, committed_amount=6_100_000, actual_amount=5_400_000),
        dict(category="Drainage", budget_amount=4_800_000, committed_amount=4_600_000, actual_amount=3_100_000),
        dict(category="Bridge Structures", budget_amount=19_000_000, committed_amount=17_500_000, actual_amount=4_900_000),
        dict(category="Paving", budget_amount=11_000_000, committed_amount=2_000_000, actual_amount=200_000),
        dict(category="Traffic & Signing", budget_amount=6_000_000, committed_amount=3_200_000, actual_amount=420_000, change_order_number="CO-002"),
    ]
    for r in rows:
        db.add(CostItem(project_id=project_id, **r))


def seed_documents(db, project, uploader_email="pm@demo.gov"):
    """Find-or-create the two sample Document rows, then *always* rewrite the
    file to local disk and re-embed it into the vector store. On a host with
    no persistent disk (e.g. Render's free tier), both the uploaded file and
    the Chroma index reset on every restart even though the Postgres Document
    row survives — so re-ingesting unconditionally on every boot is what
    keeps the RAG assistant demo working across restarts, rather than a
    one-time-only seed.
    """
    from app.models.user import User

    uploader = db.query(User).filter(User.email == uploader_email).first()

    doc_specs = [
        ("concrete_specification.txt", "Section 812 — Portland Cement Concrete (DelDOT Standard Specifications)", DocTypeEnum.spec),
        ("drainage_design_manual.txt", "Chapter 4 — Storm Drain Systems (FHWA Hydraulic Engineering Circular)", DocTypeEnum.fhwa_manual),
    ]

    for filename, title, doc_type in doc_specs:
        source_path = SAMPLE_DOCS_DIR / filename
        if not source_path.exists():
            continue

        document = (
            db.query(Document)
            .filter(Document.project_id == project.id, Document.title == title)
            .first()
        )
        if document is None:
            document = Document(
                project_id=project.id,
                title=title,
                doc_type=doc_type,
                file_path="",
                uploaded_by=uploader.id if uploader else None,
            )
            db.add(document)
            db.commit()
            db.refresh(document)

        content = source_path.read_bytes()
        file_path = ingestion.save_upload(str(project.id), str(document.id), filename, content, settings.storage_dir)
        document.file_path = file_path
        db.commit()

        ingestion.ingest_document(db, document)


def run() -> None:
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.name == DEMO_PROJECT_NAME).first()
        if project is None:
            project = seed_project(db)
            seed_rfis(db, project.id)
            seed_submittals(db, project.id)
            seed_risks(db, project.id)
            seed_ncrs(db, project.id)
            seed_safety(db, project.id)
            seed_schedule(db, project.id)
            seed_cost(db, project.id)
            db.commit()
            print(f"Seeded demo project '{DEMO_PROJECT_NAME}' with sample RFIs, submittals, risks, NCRs, "
                  f"safety issues, schedule, and cost data.")
        else:
            print(f"Demo project '{DEMO_PROJECT_NAME}' already exists — skipping PM data reseed.")

        seed_documents(db, project)
        print("Ensured sample specification documents exist and are indexed in the vector store.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
