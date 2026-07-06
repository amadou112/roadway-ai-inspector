"""Shared bootstrap/helpers for the Streamlit app. Imported by streamlit_app.py
and every page in pages/.

This is the single-process alternative to the FastAPI + Next.js stack: instead
of a REST API + separate frontend, Streamlit calls the same app.services /
app.models code directly, in-process, with no HTTP layer, no JWT, and no
separate deployment target — one Streamlit Cloud app, one free external
Postgres (e.g. Neon).
"""
import os
import sys
from pathlib import Path

import streamlit as st

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Streamlit Cloud secrets (st.secrets) aren't automatically exported as env
# vars, but app.core.config reads Settings from the environment / .env file.
# Copy them over before any app.* module (which reads settings at import
# time via get_settings()) gets imported. Real secret values always win over
# whatever (if anything) is already in the process environment.
try:
    for key, value in st.secrets.items():
        os.environ[key] = str(value)
except Exception:  # noqa: BLE001 — no secrets.toml locally, that's fine
    pass

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.enums import RoleEnum  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.user import User  # noqa: E402

DEMO_PASSWORD = "RoadwayDemo!2026"  # noqa: S105 — public demo credential, not a secret

DEMO_ACCOUNTS = [
    ("pm@demo.gov", "Alicia Torres", "Program Manager", RoleEnum.program_manager),
    ("projectmanager@demo.gov", "Marcus Webb", "Project Manager", RoleEnum.project_manager),
    ("resident-engineer@demo.gov", "Priya Nair", "Resident Engineer", RoleEnum.resident_engineer),
    ("inspector@demo.gov", "Daniel Ruiz", "Inspector", RoleEnum.inspector),
    ("designer@demo.gov", "Grace Lin", "Designer", RoleEnum.designer),
    ("contractor@demo.gov", "Tom Bradley", "Contractor", RoleEnum.contractor),
    ("executive@demo.gov", "Denise Carter", "DOT Executive", RoleEnum.dot_executive),
]

STATUS_COLORS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
    "neutral": "#898781",
}
CATEGORICAL = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
FEDERAL_BLUE = "#0b3d62"


# Only markers specific enough that they could never appear in a real,
# filled-in production connection string — "localhost" alone is NOT one of
# these, since local development legitimately points at localhost.
_PLACEHOLDER_MARKERS = ("<your", "roadway_dev_password", "your-neon", "user:pass@host")


def _diagnose_database_url(url: str) -> str | None:
    """Returns a human-readable problem description, or None if the URL at
    least *looks* like a real Postgres connection string. Catches the most
    common Streamlit Cloud misconfigurations before we ever attempt a
    connection: the DATABASE_URL secret being blank, or still holding this
    repo's local-dev default password / a copy-pasted placeholder.
    """
    if not url or not url.strip():
        return "`DATABASE_URL` is empty. Add it under Settings → Secrets for this app."
    lowered = url.lower()
    for marker in _PLACEHOLDER_MARKERS:
        if marker in lowered:
            return (
                f"`DATABASE_URL` still looks like the local-dev default or a placeholder "
                f"(contains '{marker}'). Paste your real Postgres connection string "
                f"(e.g. from neon.tech) into Settings → Secrets."
            )
    return None


def _redact_password(message: str, url: str) -> str:
    """Belt-and-suspenders: strip the literal password out of an exception
    message before it's displayed, in case the DB driver ever echoes the
    raw DSN back in an error string."""
    try:
        from sqlalchemy.engine import make_url

        password = make_url(url).password
        if password:
            message = message.replace(password, "***")
    except Exception:  # noqa: BLE001 — best-effort only
        pass
    return message


@st.cache_resource(show_spinner="Starting up Roadway AI Inspector…")
def init_app():
    """Runs once per app process: migrations, demo user/project seed, and
    real Delaware open-data ingestion. Safe to call repeatedly (every
    seed/ingest step is idempotent) but cached so Streamlit reruns don't
    repeat it on every widget interaction.

    Any failure here is caught and shown in full via st.error — Streamlit's
    default top-level handler redacts uncaught exception text (to avoid
    leaking secrets in generic cases), which hides the one thing you need to
    actually fix a bad DATABASE_URL. We print the exception type/message
    ourselves instead (never the URL itself) so the real cause is visible.
    """
    database_url = get_settings().database_url
    problem = _diagnose_database_url(database_url)
    if problem:
        st.error(f"**Can't start — database not configured.**\n\n{problem}")
        st.stop()

    try:
        cfg = Config(str(BACKEND_DIR / "alembic.ini"))
        cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        cfg.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(cfg, "head")

        from scripts import ingest_open_data, seed_demo_project, seed_roles_users

        seed_roles_users.run()
        seed_demo_project.run()
        ingest_open_data.run()
    except Exception as exc:  # noqa: BLE001 — surface it deliberately, see docstring
        safe_message = _redact_password(str(exc), database_url)
        st.error(
            "**Can't start — database setup failed.**\n\n"
            f"`{type(exc).__module__}.{type(exc).__name__}`: {safe_message}\n\n"
            "Common causes: the Postgres server is unreachable or rejecting the connection "
            "(check the host/port), the password is wrong, or the connection string is "
            "missing `?sslmode=require` (Neon requires this)."
        )
        st.stop()

    return True


def get_db():
    """Caller is responsible for closing (use `with get_db_session() as db`)."""
    return SessionLocal()


class get_db_session:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, *exc):
        self.db.close()


def apply_page_style():
    st.set_page_config(page_title="Roadway AI Inspector & Design Assistant", page_icon="🛣️", layout="wide")
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: #f4f7fb; }}
        h1, h2, h3 {{ color: {FEDERAL_BLUE}; }}
        div[data-testid="stMetricValue"] {{ color: {FEDERAL_BLUE}; }}
        section[data-testid="stSidebar"] {{ background-color: #0a1c30; }}
        section[data-testid="stSidebar"] * {{ color: #e6eef7 !important; }}
        section[data-testid="stSidebar"] .stSelectbox label {{ color: #9db3c9 !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge(label: str, tone: str | None = None) -> str:
    tone_map = {
        "open": "warning", "pending": "warning", "processing": "warning", "under_review": "warning",
        "corrective_action": "warning", "at_risk": "warning", "draft": "neutral",
        "answered": "good", "approved": "good", "completed": "good", "submitted": "good",
        "indexed": "good", "on_track": "good", "complete": "good", "mitigated": "good", "closed": "neutral",
        "rejected": "critical", "resubmit_required": "critical", "failed": "critical", "delayed": "critical",
        "low": "good", "medium": "warning", "high": "critical", "critical": "critical",
        "good": "good", "fair": "warning", "poor": "critical", "unknown": "neutral",
    }
    color = STATUS_COLORS[tone or tone_map.get(label, "neutral")]
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:999px;padding:2px 10px;font-size:0.8em;font-weight:600;text-transform:capitalize">'
        f'{label.replace("_", " ")}</span>'
    )


def render_entity_manager(
    db,
    project_id,
    model,
    title: str,
    display_columns: list[str],
    form_fields: list[tuple],
    status_field: str | None = None,
    status_options: list[str] | None = None,
    row_label_field: str = "id",
):
    """Generic list + status-update + create UI for one project-scoped entity.

    form_fields: list of (field_name, label, widget) where widget is one of
    "text", "textarea", "number", "date", or a list of options for a select.
    """
    rows = db.query(model).filter(model.project_id == project_id).order_by(model.created_at.desc()).all()

    if rows:
        table_data = []
        for r in rows:
            record = {}
            for col in display_columns:
                val = getattr(r, col, "")
                record[col.replace("_", " ").title()] = val
            table_data.append(record)
        st.dataframe(table_data, use_container_width=True, hide_index=True)
    else:
        st.caption(f"No {title.lower()} recorded yet.")

    col_update, col_create = st.columns(2)

    if status_field and rows:
        with col_update:
            st.markdown("**Update status**")
            options = [f"{getattr(r, row_label_field)}" for r in rows]
            picked = st.selectbox("Record", options, key=f"pick_{model.__name__}")
            record = rows[options.index(picked)]
            new_status = st.selectbox(
                "New status", status_options, index=status_options.index(getattr(record, status_field)),
                key=f"status_{model.__name__}",
            )
            if st.button("Save status", key=f"save_{model.__name__}"):
                setattr(record, status_field, new_status)
                db.commit()
                st.success("Updated.")
                st.rerun()

    with col_create:
        st.markdown(f"**Add new {title.lower().rstrip('s')}**")
        with st.form(key=f"form_{model.__name__}", clear_on_submit=True):
            values = {}
            for field_name, label, widget in form_fields:
                if isinstance(widget, list):
                    values[field_name] = st.selectbox(label, widget, key=f"f_{model.__name__}_{field_name}")
                elif widget == "textarea":
                    values[field_name] = st.text_area(label, key=f"f_{model.__name__}_{field_name}")
                elif widget == "number":
                    values[field_name] = st.number_input(label, value=0, key=f"f_{model.__name__}_{field_name}")
                elif widget == "date":
                    values[field_name] = st.date_input(label, key=f"f_{model.__name__}_{field_name}")
                else:
                    values[field_name] = st.text_input(label, key=f"f_{model.__name__}_{field_name}")
            if st.form_submit_button("Save"):
                obj = model(project_id=project_id, **values)
                db.add(obj)
                db.commit()
                st.success("Created.")
                st.rerun()


def sidebar_controls(db):
    st.sidebar.markdown("### 🛣️ Roadway AI Inspector")
    st.sidebar.caption("Delaware DOT Demo Environment")

    if "role_email" not in st.session_state:
        st.session_state.role_email = DEMO_ACCOUNTS[0][0]

    labels = [f"{label} — {name}" for _, name, label, _ in DEMO_ACCOUNTS]
    emails = [email for email, *_ in DEMO_ACCOUNTS]
    current_idx = emails.index(st.session_state.role_email)
    choice = st.sidebar.selectbox("Viewing as", labels, index=current_idx)
    st.session_state.role_email = emails[labels.index(choice)]

    current_user = db.query(User).filter(User.email == st.session_state.role_email).first()

    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    if not projects:
        st.sidebar.warning("No projects yet.")
        return current_user, None

    project_names = [p.name for p in projects]
    if "project_id" not in st.session_state or st.session_state.project_id not in [p.id for p in projects]:
        st.session_state.project_id = projects[0].id
    current_project_idx = [p.id for p in projects].index(st.session_state.project_id)
    project_choice = st.sidebar.selectbox("Project", project_names, index=current_project_idx)
    st.session_state.project_id = projects[project_names.index(project_choice)].id
    selected_project = next(p for p in projects if p.id == st.session_state.project_id)

    st.sidebar.divider()
    st.sidebar.caption(f"Signed in as **{current_user.full_name}**" if current_user else "")

    return current_user, selected_project
