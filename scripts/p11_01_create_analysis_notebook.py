from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "block_11_analysis.ipynb"

cells = []

def md(text):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip().splitlines(True),
    })

def code(text):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip().splitlines(True),
    })

md("""
# Block 11: Notebook Analysis

This notebook analyses the completed GDELT Southeast Asia signal pipeline using the analysis marts created in dbt.

## Purpose

The notebook supports two use cases:

1. Regional spike monitoring  
2. Country event and actor profile analysis  

Important framing: GDELT is treated as a media-coded event signal source, not as a verified ground-truth incident database.
""")

code("""
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DB_PATH = PROJECT_ROOT / "db" / "gdelt_sea.duckdb"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB_PATH))

print(f"Connected to: {DB_PATH}")
""")

md("""
## 1. Confirm available marts
""")

code("""
tables_df = con.execute(\"\"\"
    SELECT
        table_schema,
        table_name,
        table_type
    FROM information_schema.tables
    WHERE table_schema = 'marts'
    ORDER BY table_name
\"\"\").fetchdf()

tables_df
""")

md("""
## 2. Use Case 1: Regional spike monitoring

This view checks weekly event-signal volume by country and flags possible spikes using simple week-on-week logic.

Because the current project uses a controlled sample of downloaded GDELT files, the values should be treated as demonstration outputs, not final operational intelligence.
""")

code("""
regional_spike_df = con.execute(\"\"\"
    SELECT
        country_name,
        week_start_date,
        event_signal_count,
        previous_week_event_signal_count,
        week_on_week_change,
        week_on_week_ratio,
        conflict_signal_count,
        public_safety_signal_count,
        total_mentions,
        total_sources,
        total_articles,
        avg_tone,
        spike_flag
    FROM marts.mart_regional_spike_monitoring
    ORDER BY week_start_date DESC, event_signal_count DESC
\"\"\").fetchdf()

regional_spike_df
""")

code("""
regional_spike_df.to_csv(
    OUTPUT_TABLES_DIR / "regional_spike_monitoring.csv",
    index=False
)

print("Saved regional spike table.")
""")

code("""
plot_df = regional_spike_df.sort_values(["week_start_date", "country_name"])

plt.figure(figsize=(10, 5))
for country, group in plot_df.groupby("country_name"):
    plt.plot(group["week_start_date"], group["event_signal_count"], marker="o", label=country)

plt.title("Weekly GDELT event signal count by SEA country")
plt.xlabel("Week start date")
plt.ylabel("Event signal count")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

figure_path = OUTPUT_FIGURES_DIR / "weekly_event_signal_count_by_country.png"
plt.savefig(figure_path, dpi=150)
plt.show()

print(f"Saved figure to: {figure_path}")
""")

md("""
## 3. Use Case 2A: Country event profile

This view identifies dominant event codes and event classes by country.
""")

code("""
event_profile_df = con.execute(\"\"\"
    SELECT
        country_name,
        event_code_key,
        event_root_code,
        quad_class_label,
        is_conflict_quad,
        is_public_safety_signal,
        event_signal_count,
        share_of_country_events,
        country_event_rank,
        total_mentions,
        total_sources,
        total_articles,
        avg_tone
    FROM marts.mart_country_event_profile
    WHERE country_event_rank <= 10
    ORDER BY country_name, country_event_rank
\"\"\").fetchdf()

event_profile_df
""")

code("""
event_profile_df.to_csv(
    OUTPUT_TABLES_DIR / "country_event_profile_top10.csv",
    index=False
)

print("Saved country event profile table.")
""")

code("""
top_event_df = event_profile_df[event_profile_df["country_event_rank"] <= 5].copy()
top_event_df["country_event_label"] = (
    top_event_df["country_name"]
    + " | "
    + top_event_df["event_code_key"].astype(str)
)

plt.figure(figsize=(10, 6))
plt.barh(top_event_df["country_event_label"], top_event_df["event_signal_count"])
plt.title("Top event codes by country")
plt.xlabel("Event signal count")
plt.ylabel("Country | Event code")
plt.gca().invert_yaxis()
plt.tight_layout()

figure_path = OUTPUT_FIGURES_DIR / "top_event_codes_by_country.png"
plt.savefig(figure_path, dpi=150)
plt.show()

print(f"Saved figure to: {figure_path}")
""")

md("""
## 4. Use Case 2B: Country actor profile

This view identifies actors that frequently appear in each country’s media-coded event signals.

Actor labels are generated by GDELT and can be noisy. They should be used as directional signals, not clean verified entity records.
""")

code("""
actor_profile_df = con.execute(\"\"\"
    SELECT
        country_name,
        actor_position,
        COALESCE(actor_name, actor_code, actor_country_code, 'Unknown') AS actor_label,
        actor_code,
        actor_country_code,
        actor_type1_code,
        actor_event_signal_count,
        conflict_signal_count,
        public_safety_signal_count,
        country_actor_rank,
        total_mentions,
        total_sources,
        total_articles,
        avg_tone
    FROM marts.mart_country_actor_profile
    WHERE country_actor_rank <= 10
    ORDER BY country_name, country_actor_rank
\"\"\").fetchdf()

actor_profile_df
""")

code("""
actor_profile_df.to_csv(
    OUTPUT_TABLES_DIR / "country_actor_profile_top10.csv",
    index=False
)

print("Saved country actor profile table.")
""")

code("""
top_actor_df = actor_profile_df[actor_profile_df["country_actor_rank"] <= 5].copy()
top_actor_df["country_actor_label"] = (
    top_actor_df["country_name"]
    + " | "
    + top_actor_df["actor_label"].astype(str)
)

plt.figure(figsize=(10, 6))
plt.barh(top_actor_df["country_actor_label"], top_actor_df["actor_event_signal_count"])
plt.title("Top actors by country")
plt.xlabel("Actor event signal count")
plt.ylabel("Country | Actor")
plt.gca().invert_yaxis()
plt.tight_layout()

figure_path = OUTPUT_FIGURES_DIR / "top_actors_by_country.png"
plt.savefig(figure_path, dpi=150)
plt.show()

print(f"Saved figure to: {figure_path}")
""")

md("""
## 5. Summary observations

Use this section to write final project observations after reviewing the tables and charts.

Suggested framing:

- Which countries show the highest event signal volume?
- Which countries have possible spike flags?
- Which event classes dominate the sample?
- Which actors appear frequently?
- What are the limitations of using a controlled sample?
- How should public-safety stakeholders interpret these outputs?
""")

code("""
summary_df = con.execute(\"\"\"
    SELECT
        'event_rows' AS metric,
        COUNT(*) AS value
    FROM marts.fact_event_signal

    UNION ALL

    SELECT
        'countries_in_fact',
        COUNT(DISTINCT country_key)
    FROM marts.fact_event_signal

    UNION ALL

    SELECT
        'event_codes_in_fact',
        COUNT(DISTINCT event_code_key)
    FROM marts.fact_event_signal

    UNION ALL

    SELECT
        'actors_in_dim_actor',
        COUNT(*)
    FROM marts.dim_actor
\"\"\").fetchdf()

summary_df.to_csv(
    OUTPUT_TABLES_DIR / "analysis_summary_metrics.csv",
    index=False
)

summary_df
""")

code("""
con.close()
print("Notebook analysis complete.")
""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2))
print(f"Created notebook: {NOTEBOOK_PATH}")
