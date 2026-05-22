from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "gdelt_sea.duckdb"

st.set_page_config(
    page_title="RCI GDELT SEA Signal Dashboard",
    layout="wide",
)

st.title("RCI GDELT SEA Signal Dashboard")

st.caption(
    "GDELT is treated as a media-coded event signal source, not a verified incident database."
)

if not DB_PATH.exists():
    st.error(
        f"DuckDB database not found at: {DB_PATH}. "
        "Run the ingestion and dbt pipeline first before launching the dashboard."
    )
    st.stop()


@st.cache_data
def load_table(query: str) -> pd.DataFrame:
    with duckdb.connect(str(DB_PATH)) as con:
        return con.execute(query).fetchdf()


regional_df = load_table("""
    SELECT *
    FROM marts.mart_regional_spike_monitoring
    ORDER BY week_start_date DESC, event_signal_count DESC
""")

event_profile_df = load_table("""
    SELECT *
    FROM marts.mart_country_event_profile
    ORDER BY country_name, country_event_rank
""")

actor_profile_df = load_table("""
    SELECT *
    FROM marts.mart_country_actor_profile
    ORDER BY country_name, country_actor_rank
""")

summary_df = load_table("""
    SELECT
        COUNT(*) AS event_signal_rows,
        COUNT(DISTINCT country_key) AS countries,
        COUNT(DISTINCT event_code_key) AS event_codes
    FROM marts.fact_event_signal
""")


country_options = ["All"] + sorted(regional_df["country_name"].dropna().unique().tolist())

selected_country = st.sidebar.selectbox(
    "Country",
    country_options,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Local demo dashboard reading from DuckDB marts."
)

if selected_country != "All":
    regional_filtered = regional_df[regional_df["country_name"] == selected_country]
    event_filtered = event_profile_df[event_profile_df["country_name"] == selected_country]
    actor_filtered = actor_profile_df[actor_profile_df["country_name"] == selected_country]
else:
    regional_filtered = regional_df
    event_filtered = event_profile_df
    actor_filtered = actor_profile_df


st.subheader("Pipeline Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Event signal rows", int(summary_df.loc[0, "event_signal_rows"]))
col2.metric("Countries", int(summary_df.loc[0, "countries"]))
col3.metric("Event codes", int(summary_df.loc[0, "event_codes"]))

st.divider()


st.subheader("Use Case 1: Regional Spike Monitoring")

st.write(
    "Weekly country-level event signal counts, with simple week-on-week spike flags."
)

spike_chart_df = regional_filtered.copy()
spike_chart_df["week_start_date"] = pd.to_datetime(spike_chart_df["week_start_date"])

if not spike_chart_df.empty:
    chart_data = spike_chart_df.pivot_table(
        index="week_start_date",
        columns="country_name",
        values="event_signal_count",
        aggfunc="sum",
        fill_value=0,
    ).sort_index()

    st.line_chart(chart_data)
else:
    st.info("No regional spike data available for the selected filter.")

st.dataframe(
    regional_filtered[
        [
            "country_name",
            "week_start_date",
            "event_signal_count",
            "previous_week_event_signal_count",
            "week_on_week_change",
            "week_on_week_ratio",
            "conflict_signal_count",
            "public_safety_signal_count",
            "spike_flag",
        ]
    ],
    width="stretch",
)

st.divider()


st.subheader("Use Case 2A: Country Event Profile")

st.write(
    "Dominant event codes and event classes by country."
)

top_event_filtered = event_filtered[event_filtered["country_event_rank"] <= 10].copy()

st.dataframe(
    top_event_filtered[
        [
            "country_name",
            "event_code_key",
            "event_root_code",
            "quad_class_label",
            "event_signal_count",
            "share_of_country_events",
            "country_event_rank",
        ]
    ],
    width="stretch",
)

if selected_country == "All":
    top_event_chart_df = (
        top_event_filtered
        .sort_values("event_signal_count", ascending=False)
        .head(20)
        .copy()
    )
else:
    top_event_chart_df = top_event_filtered.copy()

if not top_event_chart_df.empty:
    chart_event_df = top_event_chart_df.copy()
    chart_event_df["label"] = (
        chart_event_df["country_name"]
        + " | "
        + chart_event_df["event_code_key"].astype(str)
    )

    st.bar_chart(
        chart_event_df.set_index("label")["event_signal_count"]
    )
else:
    st.info("No event profile data available for the selected filter.")

st.divider()


st.subheader("Use Case 2B: Country Actor Profile")

st.write(
    "Frequently appearing actors by country and actor position."
)

top_actor_filtered = actor_filtered[actor_filtered["country_actor_rank"] <= 10].copy()

top_actor_filtered["actor_label"] = (
    top_actor_filtered["actor_name"]
    .fillna(top_actor_filtered["actor_code"])
    .fillna(top_actor_filtered["actor_country_code"])
    .fillna("Unknown")
)

st.dataframe(
    top_actor_filtered[
        [
            "country_name",
            "actor_position",
            "actor_label",
            "actor_event_signal_count",
            "conflict_signal_count",
            "public_safety_signal_count",
            "country_actor_rank",
        ]
    ],
    width="stretch",
)

if selected_country == "All":
    top_actor_chart_df = (
        top_actor_filtered
        .sort_values("actor_event_signal_count", ascending=False)
        .head(20)
        .copy()
    )
else:
    top_actor_chart_df = top_actor_filtered.copy()

if not top_actor_chart_df.empty:
    chart_actor_df = top_actor_chart_df.copy()
    chart_actor_df["label"] = (
        chart_actor_df["country_name"]
        + " | "
        + chart_actor_df["actor_label"].astype(str)
    )

    st.bar_chart(
        chart_actor_df.set_index("label")["actor_event_signal_count"]
    )
else:
    st.info("No actor profile data available for the selected filter.")

st.divider()


st.subheader("Limitations")

st.markdown(
    """
- Current outputs are based on the locally downloaded sample, not necessarily the full 90-day universe.
- GDELT is a media-coded event signal source, not verified ground truth.
- Actor labels and event codes can be noisy and should be interpreted directionally.
- The spike flag is a simple demonstration rule, not a production alerting model.
- This dashboard is designed as a local project demonstration layer, not a deployed production application.
"""
)
