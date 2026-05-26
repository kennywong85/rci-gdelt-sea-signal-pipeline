# Final Demo Checklist

This checklist is used to confirm that the RCI GDELT SEA Signal Pipeline is ready for demonstration or project defence.

## 1. Repository Health

Run from project root:

```bash
git status
```

Expected:

```text
nothing to commit, working tree clean
```

## 2. Core Pipeline Health

Run the pipeline using existing local files:

```bash
python scripts/run_pipeline.py --days 90 --max-files 14 --skip-download
```

Expected final output:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

## 3. dbt Health Check

Run from the dbt project folder:

```bash
cd dbt/gdelt_sea
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Expected test result:

```text
PASS=60
WARN=0
ERROR=0
TOTAL=60
```

## 4. DuckDB Warehouse Check

The local warehouse file should exist:

```text
db/gdelt_sea.duckdb
```

Important warehouse objects:

```text
metadata.sea_country_lookup
raw.gdelt_events

staging.stg_gdelt_events
staging.stg_sea_countries

marts.dim_date
marts.dim_country
marts.dim_event_code
marts.dim_actor
marts.fact_event_signal

marts.mart_regional_spike_monitoring
marts.mart_country_event_profile
marts.mart_country_actor_profile
```

## 5. Notebook Check

Notebook location:

```text
notebooks/block_11_analysis.ipynb
```

Purpose:

- inspect row counts
- preview regional spike monitoring
- preview country event profile
- preview country actor profile

## 6. Dashboard Check

Run from project root:

```bash
streamlit run dashboard/app.py
```

If needed:

```bash
python -m streamlit run dashboard/app.py
```

Expected:

- dashboard opens locally
- country filter works
- regional spike monitoring section loads
- country event profile section loads
- country actor profile section loads

## 7. Documentation Check

Important documents:

```text
README.md
docs/architecture.md
docs/data_lineage.md
docs/schema_overview.md
docs/defence_notes.md
docs/local_scheduled_refresh.md
docs/presentation_outline.md
docs/final_demo_checklist.md
```

## 8. Key Defence Reminders

Use careful language.

Say:

```text
media-coded event signals
event signal volume
public-safety-related signals
directional monitoring
further investigation
```

Avoid overclaiming:

```text
verified incidents
confirmed conflict counts
real-time intelligence
production alerting system
```

## 9. Final Demo Story

The recommended demo flow is:

1. Start with the project purpose and use case.
2. Explain GDELT as a media-coded event signal source.
3. Show the architecture.
4. Explain the local DuckDB warehouse.
5. Explain dbt staging, star schema and marts.
6. Show dbt test result.
7. Show notebook outputs.
8. Show Streamlit dashboard.
9. Explain limitations and future extensions.

## 10. Current Implementation Status

Current implementation is complete through Block 17.

Blocks 18 and 19 are optional future extensions for BigQuery smoke-test or comparison notes.