import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st
from sqlalchemy import func

from streamlit_common import STATUS_COLORS, apply_page_style, get_db_session, init_app, sidebar_controls

apply_page_style()
init_app()

from app.models.enums import BridgeConditionEnum  # noqa: E402
from app.models.opendata import Bridge, CrashRecord, PavementSegment  # noqa: E402

st.title("Bridge & Roadway Data Dashboard")
st.caption(
    "Live National Bridge Inventory (NBI), FARS crash, and pavement condition data for Delaware "
    "(FHWA/USDOT open data)."
)

CONDITION_COLOR = {
    "good": [12, 163, 12],
    "fair": [250, 178, 25],
    "poor": [208, 59, 59],
    "unknown": [137, 135, 129],
}

with get_db_session() as db:
    sidebar_controls(db)

    condition_counts = dict(db.query(Bridge.condition, func.count(Bridge.id)).group_by(Bridge.condition).all())
    total_bridges = sum(condition_counts.values())
    avg_year = db.query(func.avg(Bridge.year_built)).scalar()
    total_crashes = db.query(func.count(CrashRecord.id)).scalar() or 0
    total_fatalities = db.query(func.coalesce(func.sum(CrashRecord.fatalities), 0)).scalar() or 0
    avg_iri = db.query(func.avg(PavementSegment.iri)).scalar()
    counties = sorted([c[0] for c in db.query(Bridge.county).distinct().all() if c[0]])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bridges", total_bridges)
    col2.metric("Poor Condition", condition_counts.get(BridgeConditionEnum.poor, 0))
    col3.metric("Avg. Year Built", int(avg_year) if avg_year else "—")
    col4.metric("Crashes Recorded", total_crashes, f"{int(total_fatalities)} fatalities" if total_fatalities else None)

    st.divider()
    county_filter = st.selectbox("Filter by County", ["All Counties"] + counties)

    query = db.query(Bridge)
    if county_filter != "All Counties":
        query = query.filter(Bridge.county == county_filter)
    bridges = query.all()

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Bridge Locations")
        map_rows = [
            {
                "lat": b.latitude, "lon": b.longitude, "name": b.facility_carried or "Unnamed structure",
                "feature": b.feature_intersected or "—", "year": b.year_built, "condition": b.condition.value,
                "color": CONDITION_COLOR[b.condition.value],
            }
            for b in bridges
            if b.latitude and b.longitude
        ]
        if map_rows:
            df = pd.DataFrame(map_rows)
            layer = pdk.Layer(
                "ScatterplotLayer", df, get_position="[lon, lat]", get_fill_color="color",
                get_radius=150, pickable=True,
            )
            view_state = pdk.ViewState(latitude=df["lat"].mean(), longitude=df["lon"].mean(), zoom=8)
            st.pydeck_chart(
                pdk.Deck(
                    layers=[layer], initial_view_state=view_state, map_style=None,
                    tooltip={"text": "{name}\nover {feature}\nBuilt {year} · {condition}"},
                )
            )
        else:
            st.caption("No bridge location data for this filter.")

    with right:
        st.subheader("Condition Distribution")
        fig = px.bar(
            x=["Good", "Fair", "Poor", "Unknown"],
            y=[
                condition_counts.get(BridgeConditionEnum.good, 0),
                condition_counts.get(BridgeConditionEnum.fair, 0),
                condition_counts.get(BridgeConditionEnum.poor, 0),
                condition_counts.get(BridgeConditionEnum.unknown, 0),
            ],
            color=["Good", "Fair", "Poor", "Unknown"],
            color_discrete_map={
                "Good": STATUS_COLORS["good"], "Fair": STATUS_COLORS["warning"],
                "Poor": STATUS_COLORS["critical"], "Unknown": STATUS_COLORS["neutral"],
            },
            labels={"x": "", "y": "Bridges"},
        )
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Crashes by Year (FARS)")
    crash_rows = (
        db.query(CrashRecord.case_year, func.count(CrashRecord.id)).group_by(CrashRecord.case_year).order_by(CrashRecord.case_year).all()
    )
    if crash_rows:
        fig2 = px.bar(
            x=[str(y) for y, _ in crash_rows], y=[c for _, c in crash_rows],
            labels={"x": "Year", "y": "Crashes"}, color_discrete_sequence=[STATUS_COLORS["critical"]],
        )
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("No crash data available (FARS endpoint may be unreachable from this network).")
