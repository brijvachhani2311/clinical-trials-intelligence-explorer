"""
Clinical Trials Intelligence Explorer — Streamlit Dashboard
=================================================================
Interactive dashboard over the normalized trials.db built in sql/build_db.py.

USAGE:
    streamlit run dashboard.py
(run from inside the app/ folder, or adjust DB_PATH below)
"""

import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# Anchor the DB path to this script's own location, not the working
# directory — Streamlit Cloud runs the app from a different working
# directory than a local `streamlit run` from inside app/, so a plain
# relative path like "../data/trials.db" breaks in deployment even
# though it works locally.
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "trials.db"

st.set_page_config(page_title="Clinical Trials Intelligence Explorer", layout="wide")


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    trials = pd.read_sql("SELECT * FROM trials", conn)
    phases = pd.read_sql("SELECT * FROM trial_phases", conn)
    cities = pd.read_sql("SELECT * FROM trial_germany_cities", conn)
    conn.close()
    trials["start_year"] = pd.to_numeric(trials["start_date"].str[:4], errors="coerce")
    return trials, phases, cities


trials, phases, cities = load_data()

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.header("Filters")

areas = sorted(trials["search_condition"].unique())
selected_areas = st.sidebar.multiselect("Therapeutic area", areas, default=areas)

statuses = sorted(trials["status"].unique())
selected_statuses = st.sidebar.multiselect("Status", statuses, default=statuses)

year_min, year_max = int(trials["start_year"].min()), int(trials["start_year"].max())
year_range = st.sidebar.slider("Trial start year", year_min, year_max, (2005, year_max))

filtered = trials[
    trials["search_condition"].isin(selected_areas)
    & trials["status"].isin(selected_statuses)
    & trials["start_year"].between(*year_range)
]

# ---------------------------------------------------------------
# Header + headline insight
# ---------------------------------------------------------------
st.title("🧪 Clinical Trials Intelligence Explorer")
st.caption(
    "Clinical trials with at least one German site, across seven therapeutic areas. "
    "Data: ClinicalTrials.gov public API v2."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Trials (filtered)", f"{len(filtered):,}")
col2.metric("Unique sponsors", f"{filtered['lead_sponsor'].nunique():,}")
col3.metric("German cities", f"{cities[cities['nct_id'].isin(filtered['nct_id'])]['city'].nunique():,}")
term_rate = (filtered["status"] == "TERMINATED").mean() if len(filtered) else 0
col4.metric("Termination rate", f"{term_rate:.1%}")

st.info(
    "**Headline finding:** non-small cell lung cancer trials terminate early at ~15% — "
    "more than double the rate for COPD or type 2 diabetes (~6%). Consistent with oncology "
    "trials' higher exposure to futility stops and a fast-moving competitive landscape."
)

# ---------------------------------------------------------------
# Charts
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Trends over time", "Sponsor landscape", "Phase breakdown", "Geography"]
)

with tab1:
    yearly = (
        filtered.groupby(["start_year", "search_condition"])
        .size()
        .reset_index(name="n_trials")
    )
    fig = px.line(
        yearly, x="start_year", y="n_trials", color="search_condition",
        markers=True, title="Trial Starts per Year by Therapeutic Area",
        labels={"start_year": "Year", "n_trials": "Trials started", "search_condition": "Area"},
    )
    st.plotly_chart(fig, width="stretch")

    term_by_area = (
        filtered.groupby("search_condition")
        .apply(lambda x: (x["status"] == "TERMINATED").mean())
        .sort_values(ascending=False)
        .reset_index(name="termination_rate")
    )
    fig2 = px.bar(
        term_by_area, x="search_condition", y="termination_rate",
        title="Termination Rate by Therapeutic Area",
        labels={"search_condition": "Area", "termination_rate": "Termination rate"},
    )
    fig2.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig2, width="stretch")

with tab2:
    top_sponsors = (
        filtered["lead_sponsor"].value_counts().head(15).reset_index()
    )
    top_sponsors.columns = ["sponsor", "n_trials"]
    fig3 = px.bar(
        top_sponsors, x="n_trials", y="sponsor", orientation="h",
        title="Top 15 Sponsors by Trial Count",
    )
    fig3.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, width="stretch")

    class_split = filtered["lead_sponsor_class"].value_counts().reset_index()
    class_split.columns = ["sponsor_class", "n_trials"]
    fig4 = px.pie(class_split, names="sponsor_class", values="n_trials", title="Sponsor Class Split")
    st.plotly_chart(fig4, width="stretch")

with tab3:
    ph = phases[phases["nct_id"].isin(filtered["nct_id"])]
    ph_merged = ph.merge(filtered[["nct_id", "lead_sponsor_class"]], on="nct_id")
    phase_order = ["EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4"]
    ph_merged = ph_merged[ph_merged["phase"].isin(phase_order)]
    fig5 = px.histogram(
        ph_merged, x="phase", color="lead_sponsor_class",
        category_orders={"phase": phase_order},
        title="Trial Phase by Sponsor Class",
    )
    st.plotly_chart(fig5, width="stretch")

with tab4:
    city_counts = (
        cities[cities["nct_id"].isin(filtered["nct_id"])]["city"]
        .value_counts().head(15).reset_index()
    )
    city_counts.columns = ["city", "n_trials"]
    fig6 = px.bar(
        city_counts, x="n_trials", y="city", orientation="h",
        title="Top 15 German Cities by Trial Site Count",
    )
    fig6.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig6, width="stretch")

st.divider()
st.caption(
    "Built by [Your Name] — data cleaning, SQL schema, and analysis at "
    "github.com/brijvachhani2311/clinical-trials-intelligence-explorer"
)
