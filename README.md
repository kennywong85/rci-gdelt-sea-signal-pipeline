# RCI GDELT SEA Signal Pipeline

## Project Purpose

This project builds a local data engineering pipeline using GDELT 2.0 Events data to monitor public-safety-related event signals across Southeast Asia.

The project is designed as both:

1. A DSAI Module 2 data engineering learning scaffold.
2. A reusable early Red Cloud Intelligence pipeline prototype.

## Core Question

How can public-safety stakeholders monitor evolving conflict and disorder signals across Southeast Asia using regularly refreshed open news-event data?

## Important Data Framing

GDELT is used as a media-coded event signal source.

This project should not present GDELT as a verified ground-truth incident database. Outputs should use cautious language such as:

- signals
- media-coded events
- event signal volume
- possible spike
- areas for further investigation

This project is a data engineering and signal-monitoring prototype, not an operational intelligence system.

## Scope

- Source: GDELT 2.0 Events files
- Geography: Southeast Asia
- Time window design: Rolling 90 days
- Current build mode: Controlled local sample
- Warehouse: DuckDB
- ELT: dbt + dbt-duckdb
- Analysis: Python / Jupyter
- Presentation layer: Local Streamlit dashboard
- Optional extension areas:
  - Spark batch-processing notebook
  - Local orchestration runner
  - Local scheduled refresh
  - BigQuery public dataset smoke test / comparison

## Primary Use Cases

### Use Case 1: Regional Spike Monitoring

Identify which Southeast Asian countries show rising or unusual public-safety-related event signal volume.

### Use Case 2: Event and Actor Profile

For countries with elevated signals, identify the event categories and actor patterns that dominate.

## Current MVP Status

Core MVP completed through Block 12.

The completed MVP demonstrates:

```text
GDELT source discovery
    ↓
Rolling 90-day file inventory
    ↓
Download manifest
    ↓
Controlled downloader
    ↓
Local raw GDELT CSV files
    ↓
DuckDB raw table
    ↓
dbt staging views
    ↓
dbt star schema marts
    ↓
dbt analysis marts
    ↓
dbt data quality tests
    ↓
Jupyter notebook analysis
    ↓
Local Streamlit dashboard
## Repository Structure

```text
.
├── dashboard/
│   └── app.py
├── data/
│   ├── lookup/
│   ├── processed/
│   └── raw/
├── db/
├── dbt/
│   └── gdelt_sea/
├── docs/
├── logs/
├── notebooks/
│   └── block_11_analysis.ipynb
├── outputs/
│   ├── figures/
│   └── tables/
├── scripts/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt

## Current Implementation Status

The formal implementation plan uses broader project blocks. Our live coding work used smaller prototype scripts, especially for the early ingestion pipeline. The status below is aligned to the latest implementation plan stages.

### Block 0: Project setup and repo skeleton

Status: Completed.

Completed work:

- Created project repository and folder structure.
- Added README.md, requirements.txt, .env.example and .gitignore.
- Set up project folders for data, database, scripts, dbt, notebooks, outputs, docs and logs.
- Confirmed project opens correctly in VS Code / WSL.

### Block 1: Environment and package setup

Status: Completed for current MVP scope.

Completed work:

- Confirmed use of the `elt` conda environment.
- Installed/verified core packages including DuckDB, pandas, requests, dbt-core and dbt-duckdb.
- Registered `Python (elt)` as a Jupyter kernel.
- Confirmed Python scripts and notebooks can run inside the project.

Future extension:

- Confirm Spark environment separately if continuing to the Spark demo block.

### Block 2: GDELT source discovery and 90-day file manifest

Status: Completed.

Completed work:

- Confirmed GDELT master file list is reachable.
- Confirmed GDELT 2.0 Events files can be identified using `.export.CSV.zip`.
- Confirmed latest GDELT 2.0 Events file can be downloaded and unzipped.
- Confirmed DuckDB can read the raw tab-delimited GDELT event file.
- Built rolling 90-day file inventory from the GDELT master file list.
- Parsed timestamps from GDELT 2.0 Events filenames.
- Confirmed expected rolling 90-day file window of 8,640 event files.
- Saved generated local inventory output to `data/processed/`.

Related live scripts:

```text
scripts/p02_01_gdelt_source_smoke_test.py
scripts/p02_02_gdelt_90day_inventory.py
```

### Block 3: Raw download and landing zone

Status: Completed for controlled sample download.

Completed work:

- Built download manifest comparing expected rolling-window GDELT files against local files.
- Added local file status flags:
  - missing
  - zip_downloaded_not_extracted
  - ready
- Created foundation for incremental downloading and scheduled refresh.
- Added new-file-only download logic using the rolling-window manifest.
- Added controlled max-file download limit for safe testing.
- Added automatic extraction from ZIP to raw CSV.
- Confirmed repeated runs do not need to redownload already-ready files.

Current sample state:

- 14 GDELT ZIP files downloaded.
- 14 GDELT CSV files extracted.
- 14 files marked ready for loading.

Related live scripts:

```text
scripts/p03_01_gdelt_download_manifest.py
scripts/p03_02_gdelt_controlled_downloader.py
```

### Block 4: DuckDB file-query and SEA filtering prototype

Status: Completed.

Completed work:

- Defined GDELT 2.0 Events column names.
- Created Southeast Asia country lookup file.
- Confirmed DuckDB can filter GDELT rows using `ActionGeo_CountryCode`.
- Confirmed Southeast Asia event signals can be isolated from global GDELT files.
- Confirmed DuckDB can read raw GDELT files directly without using Polars.

SEA lookup file:

```text
data/lookup/sea_country_codes.csv
```

Related live script:

```text
scripts/p04_01_gdelt_sea_filter_test.py
```

### Block 5: Load raw table into DuckDB

Status: Completed for current controlled sample.

Completed work:

- Created local DuckDB database:

```text
db/gdelt_sea.duckdb

### Block 6: dbt-duckdb project setup

Status: Completed.

Completed work:

- Initialised dbt project under:

```text
dbt/gdelt_sea/
```

- Create `profiles.yml.example`.
- Run `dbt debug`.
- Create first simple staging model selecting from `raw.gdelt_events`.
- Run `dbt run`.
- Confirm dbt can create a model inside DuckDB.

### Block 7: Staging models

Status: Completed.

Completed work:

- Expanded `staging.stg_gdelt_events` into a fuller cleaned and typed staging model.
- Standardised raw GDELT field names into readable snake_case.
- Parsed event dates and derived:
  - `event_week_start`
  - `event_month_start`
- Added event classification fields:
  - `quad_class_label`
  - `is_conflict_quad`
  - `is_public_safety_signal`
- Created `staging.stg_sea_countries` from the Southeast Asia country lookup table.
- Added dbt source definitions for:
  - `raw.gdelt_events`
  - `metadata.sea_country_lookup`
- Ran `dbt run --select staging` successfully.
- Ran `dbt test --select staging` successfully.
- Confirmed 13 dbt tests passed.
- Confirmed staging row counts:
  - `staging.stg_gdelt_events`: 457 rows.
  - `staging.stg_sea_countries`: 11 rows.

### Block 8: Star schema dimensions and fact table

Status: Completed.

Completed work:

- Created star schema mart models:
  - `marts.dim_date`
  - `marts.dim_country`
  - `marts.dim_event_code`
  - `marts.dim_actor`
  - `marts.fact_event_signal`
- Built `fact_event_signal` as the central fact table with one row per GDELT event signal.
- Linked fact rows to date, country, event code and actor dimensions.
- Preserved core GDELT measures:
  - `event_count`
  - `num_mentions`
  - `num_sources`
  - `num_articles`
  - `avg_tone`
  - `goldstein_scale`
- Ran `dbt run --select marts` successfully.
- Ran `dbt test --select marts` successfully.
- Confirmed 22 dbt mart tests passed.
- Confirmed marts row counts:
  - `marts.dim_date`: 4 rows.
  - `marts.dim_country`: 11 rows.
  - `marts.dim_event_code`: 56 rows.
  - `marts.dim_actor`: 176 rows.
  - `marts.fact_event_signal`: 457 rows.
- Confirmed the warehouse now has raw, staging and marts layers.

### Block 9: Analysis marts for two use cases

Status: Completed.

Completed work:

- Created use-case-specific analysis mart models:
  - `marts.mart_regional_spike_monitoring`
  - `marts.mart_country_event_profile`
  - `marts.mart_country_actor_profile`
- Built `mart_regional_spike_monitoring` for weekly country-level event signal monitoring.
- Built `mart_country_event_profile` for identifying dominant event codes and event classes by country.
- Built `mart_country_actor_profile` for identifying frequently appearing actors by country.
- Added simple week-on-week spike logic using prior-week comparison.
- Added country-level event ranking logic.
- Added country-level actor ranking logic.
- Ran `dbt run` successfully for the analysis marts.
- Ran `dbt test` successfully for the analysis marts.
- Confirmed analysis mart row counts:
  - `marts.mart_regional_spike_monitoring`: 11 rows.
  - `marts.mart_country_event_profile`: 150 rows.
  - `marts.mart_country_actor_profile`: 304 rows.

### Block 10: Data quality tests

Status: Completed.

Completed work:

- Added custom dbt SQL tests under `dbt/gdelt_sea/tests/`.
- Added row-count reconciliation across raw, staging and fact layers.
- Added test to detect future event dates.
- Added test to validate event week/month derivations.
- Added test to ensure count-like metrics are non-negative.
- Added test to ensure `event_count` is always 1 in the fact table.
- Added test to ensure staged events remain within the Southeast Asia country scope.
- Added test to ensure analysis marts are not empty.
- Added relationship tests from `fact_event_signal` to dimension tables.
- Ran full dbt model rebuild successfully using `dbt run --profiles-dir .`.
- Ran full dbt test suite successfully using `dbt test --profiles-dir .`.
- Confirmed final data quality result:
  - PASS: 60
  - WARN: 0
  - ERROR: 0
  - TOTAL: 60

### Block 11: Notebook analysis

Status: Completed.

Completed work:

- Created analysis notebook:
  - `notebooks/block_11_analysis.ipynb`
- Created notebook generator script:
  - `scripts/p11_01_create_analysis_notebook.py`
- Queried completed analysis marts from DuckDB.
- Produced analysis outputs under `outputs/`.
- Covered both project use cases:
  - Regional spike monitoring.
  - Country event and actor profile analysis.
- Confirmed notebook runs successfully using the `Python (elt)` kernel.
- Confirmed summary metrics:
  - `event_rows`: 457
  - `countries_in_fact`: 9
  - `event_codes_in_fact`: 56
  - `actors_in_dim_actor`: 176

### Block 12: Simple Streamlit dashboard

Status: Completed.

Completed work:

- Created local Streamlit dashboard:
  - `dashboard/app.py`
- Dashboard reads from local DuckDB database:
  - `db/gdelt_sea.duckdb`
- Dashboard uses marts-layer outputs for:
  - Pipeline summary metrics.
  - Regional spike monitoring.
  - Country event profile.
  - Country actor profile.
- Added country filter for simple stakeholder exploration.
- Added limitations section to frame GDELT as a media-coded signal source.
- Confirmed dashboard runs locally using:
  - `streamlit run dashboard/app.py`
- Confirmed browser refresh and country filter interactions work without crashing.

### Block 13: Spark distributed batch demonstration

Status: Planned.

Planned work:

- Create a controlled Spark demo notebook.
- Read a manageable subset of raw GDELT files.
- Apply SEA filtering and basic aggregation.
- Compare Spark distributed batch pattern against the DuckDB core pipeline.

### Block 14: One-command orchestration runner

Status: Planned.

Planned work:

- Create `scripts/run_pipeline.py`.
- Chain extraction, raw loading, dbt build/test and quality checks into one repeatable command.

### Block 15: Local scheduled refresh

Status: Planned.

Planned work:

- Use Windows Task Scheduler or WSL cron.
- Schedule local refresh after one-command pipeline is stable.

### Block 16: Documentation and architecture diagrams

Status: Planned.

Planned work:

- Write architecture, data lineage, data dictionary and schema justification docs.
- Create architecture diagrams.

### Block 17: Final packaging and presentation readiness

Status: Planned.

Planned work:

- Clean repo.
- Confirm no large generated files are committed.
- Prepare final project story, limitations and backup submission materials.

### Block 18: BigQuery public dataset smoke test

Status: Planned / end-of-project demo.

Planned work:

- Revisit GDELT BigQuery access after the core CSV/DuckDB pipeline works.
- Run a small smoke-test query against the public GDELT dataset if setup permits.
- Keep this as a learning extension, not the core pipeline.

### Block 19: BigQuery versus CSV/DuckDB comparison

Status: Planned / end-of-project comparison.

Planned work:

- Compare the BigQuery route against the local CSV/DuckDB route.
- Explain trade-offs:
  - managed cloud warehouse convenience
  - local reproducibility
  - cost/control considerations
  - ingestion learning value
  - scale and performance implications

## Generated Files Not Committed to Git

The following are generated/local files and should not be committed:

```text
data/raw/
data/processed/
db/*.duckdb
db/*.duckdb.wal
logs/
outputs/
```

These are ignored through `.gitignore`.

## Current Scripts

```text
scripts/p02_01_gdelt_source_smoke_test.py
scripts/p04_01_gdelt_sea_filter_test.py
scripts/p02_02_gdelt_90day_inventory.py
scripts/p03_01_gdelt_download_manifest.py
scripts/p03_02_gdelt_controlled_downloader.py
scripts/p05_01_load_raw_gdelt_to_duckdb.py
```

## Current Learning Summary

So far, the project has proven:

1. GDELT source discovery works.
2. GDELT event file URLs can be identified from the master file list.
3. A rolling 90-day file inventory can be built.
4. Missing/local/ready file status can be tracked.
5. Controlled file download and extraction works.
6. DuckDB can read raw GDELT files directly.
7. Southeast Asia filtering works using `ActionGeo_CountryCode`.
8. SEA-filtered rows can be loaded into a DuckDB raw table.

## Next Step

Proceed to:

```text
Project pit stop: loose-end review and Blocks 0–12 defence walkthrough
```

Before continuing to optional Spark, orchestration and scheduling blocks, the next step is to review loose ends and create a clear explanation of how Blocks 0–12 fit together.
