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
- Optional technical demonstration: Spark batch-processing notebook

## Primary Use Cases

### Use Case 1: Regional Spike Monitoring

Identify which Southeast Asian countries show rising or unusual public-safety-related event signals.

### Use Case 2: Event and Actor Profile

For countries with elevated signals, identify the event categories and actor patterns that dominate.

## Project Status

- Block 0: Project scaffold and environment setup completed.
  - Created repo structure.
  - Added README, requirements.txt, .env.example and .gitignore.
  - Set up project folders for data, database, scripts, dbt, notebooks, outputs, docs and logs.

- Block 1: GDELT source smoke test completed.
  - Confirmed GDELT master file list is reachable.
  - Confirmed latest GDELT 2.0 Events file can be downloaded and unzipped.
  - Confirmed DuckDB can read the raw tab-delimited GDELT event file.

- Block 2: Southeast Asia country filter test completed.
  - Created SEA country lookup file.
  - Confirmed DuckDB can filter GDELT rows using ActionGeo_CountryCode.
  - Confirmed Southeast Asia event signals can be isolated from global GDELT files.

- Block 3: Rolling 90-day GDELT file inventory completed.
  - Built inventory logic from the GDELT master file list.
  - Parsed timestamps from GDELT 2.0 Events filenames.
  - Confirmed expected rolling 90-day file window of 8,640 event files.
  - Saved generated local inventory output to data/processed/.

- Block 4: Download manifest and new-file-only logic completed.
  - Built manifest comparing expected rolling-window GDELT files against local files.
  - Added local file status flags for missing, downloaded-not-extracted, and ready files.
  - Created foundation for incremental downloading and scheduled refresh.

- Block 5: Controlled GDELT downloader completed.
  - Added new-file-only download logic using the rolling-window manifest.
  - Added controlled max-file download limit for safe testing.
  - Added automatic extraction from ZIP to raw CSV.
  - Confirmed local status updates from missing to ready.

- Block 6: DuckDB raw table load completed.
  - Loaded ready GDELT CSV files into local DuckDB warehouse.
  - Created metadata.sea_country_lookup reference table.
  - Created raw.gdelt_events table filtered to Southeast Asia using ActionGeo_CountryCode.
  - Confirmed raw table is ready for downstream staging and dbt transformation.

Next: Block 7 — initialize dbt project and connect dbt-duckdb to the local warehouse.

