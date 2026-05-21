# RCI GDELT SEA Signal Pipeline

## Project Purpose

This project builds a local data engineering pipeline using GDELT 2.0 Events data to monitor public-safety-related event signals across Southeast Asia.

The project is designed as both:

1. A DSAI Module 2 data engineering learning scaffold.
2. A reusable early Red Cloud Intelligence pipeline prototype.

## Core Question

How can public-safety stakeholders monitor evolving conflict and disorder signals across Southeast Asia using regularly refreshed open news-event data?

## Scope

- Source: GDELT 2.0 Events files
- Geography: Southeast Asia
- Time window: Rolling 90 days
- Warehouse: DuckDB
- ELT: dbt + dbt-duckdb
- Orchestration: Local scheduled refresh
- Analysis: Python / Jupyter
- Optional presentation layer: Streamlit dashboard
- Optional technical demonstrations:
  - Spark batch-processing notebook
  - BigQuery public dataset smoke test / comparison

## Primary Use Cases

### Use Case 1: Regional Spike Monitoring

Identify which Southeast Asian countries show rising or unusual public-safety-related event signals.

### Use Case 2: Event and Actor Profile

For countries with elevated signals, identify the event categories and actor patterns that dominate.

## Important Data Framing

GDELT is used as a media-coded event signal source.

This project should not present GDELT as a verified ground-truth incident database. Outputs should use cautious language such as "signals", "media-coded events", "event signal volume", and "areas for further investigation".

## Current Architecture

Current working flow:

```text
GDELT 2.0 master file list
    ↓
Rolling 90-day file inventory
    ↓
Download manifest
    ↓
Controlled downloader
    ↓
Local raw GDELT CSV files
    ↓
DuckDB file query
    ↓
Southeast Asia filter using ActionGeo_CountryCode
    ↓
DuckDB raw table: raw.gdelt_events
```

Current local DuckDB database:

```text
db/gdelt_sea.duckdb
```

Current DuckDB tables:

```text
metadata.sea_country_lookup
raw.gdelt_events
staging.stg_gdelt_events
```

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

Status: Mostly completed.

Completed work:

- Confirmed use of the `elt` conda environment.
- Installed/verified core packages including DuckDB, pandas, requests, dbt-core and dbt-duckdb.
- Confirmed Python scripts can run inside the project.

Remaining work:

- Add fuller setup notes later in documentation.
- Confirm Spark environment separately when reaching the Spark demo block.

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

### Block 5: Load raw table and ingestion metadata into DuckDB

Status: Partially completed.

Completed work:

- Created local DuckDB database:

```text
db/gdelt_sea.duckdb
```

- Created metadata reference table:

```text
metadata.sea_country_lookup
```

- Created raw GDELT event table:

```text
raw.gdelt_events
```

- Loaded ready GDELT CSV files into the local DuckDB warehouse.
- Created `raw.gdelt_events` table filtered to Southeast Asia using `ActionGeo_CountryCode`.
- Confirmed sample load result:
  - 14 ready CSV files.
  - 13,726 global rows read.
  - 450 Southeast Asia rows loaded into `raw.gdelt_events`.
- Confirmed raw table is ready for downstream staging and dbt transformation.

Related live script:

```text
scripts/p05_01_load_raw_gdelt_to_duckdb.py
```

Remaining work:

- Add proper ingestion metadata tables later:
  - `metadata.file_manifest`
  - `metadata.ingestion_runs`
- Add deduplication strategy for repeated/full refreshes.

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

Status: Planned.

Planned work:

- Clean, type and standardise raw GDELT fields.
- Parse event dates and date-added timestamps.
- Rename raw GDELT fields into readable snake_case.
- Standardise Southeast Asia country names/codes.
- Keep event codes, actor fields, geography fields and metrics needed for analysis.

### Block 8: Star schema dimensions and fact table

Status: Planned.

Planned work:

- Build dimensional warehouse tables:
  - `dim_date`
  - `dim_country`
  - `dim_event_code`
  - `dim_actor`
  - optional `dim_geo`
- Build central fact table:
  - `fact_event_signal`

### Block 9: Analysis marts for two use cases

Status: Planned.

Planned work:

- Build mart tables for:
  - regional spike monitoring
  - country/event profile
  - country/actor profile

### Block 10: Data quality tests

Status: Planned.

Planned work:

- Add dbt and custom tests for:
  - non-null event IDs
  - unique event IDs in the final fact table
  - valid dates
  - SEA country scope
  - known event codes
  - non-negative metrics
  - zero-row pipeline checks

### Block 11: Notebook analysis

Status: Planned.

Planned work:

- Build Jupyter notebook that reads from marts.
- Produce tables and charts for the two agreed use cases.

### Block 12: Simple Streamlit dashboard

Status: Planned / optional.

Planned work:

- Build a thin local dashboard after notebook outputs are stable.
- Keep dashboard simple: country selector, date selector, weekly signal trend, top event categories and actor patterns.

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
Block 7: Staging models
```

This will move the project from raw ingestion into the ELT transformation layer.
