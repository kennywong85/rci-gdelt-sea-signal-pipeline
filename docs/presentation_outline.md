# Presentation Outline

This outline supports a short project presentation or defence walkthrough.

## 1. Opening Summary

This project builds a local data engineering pipeline using GDELT 2.0 Events data to monitor media-coded public-safety-related event signals across Southeast Asia.

The project follows an ELT pattern:

```text
Extract → Load → Transform
```

Python handles extraction and raw loading. DuckDB acts as the local analytical warehouse. dbt handles transformation and data quality tests. Notebook and Streamlit layers are used for analysis and presentation.

## 2. Problem Framing

Public-safety and security teams often need early directional indicators of emerging disorder, conflict or public-safety-related signals.

GDELT provides high-frequency, media-coded event data that can be used as a signal source.

Important caveat:

GDELT should not be treated as verified ground truth. It is better interpreted as a noisy but useful monitoring signal.

## 3. Data Source

Data source:

```text
GDELT 2.0 Events
```

The project uses GDELT event files from the public file list.

The ingestion design supports a rolling 90-day file inventory.

For MVP safety, the pipeline uses a controlled local sample instead of downloading the full file universe.

## 4. Geographic Scope

The project focuses on Southeast Asia.

The scope is defined through:

```text
data/lookup/sea_country_codes.csv
```

The project filters by:

```text
ActionGeo_CountryCode
```

This means events are scoped by event location, not actor nationality.

## 5. Pipeline Architecture

High-level flow:

```text
GDELT file list
→ rolling 90-day inventory
→ download manifest
→ controlled downloader
→ local raw files
→ DuckDB raw load
→ dbt staging
→ dbt star schema
→ analysis marts
→ notebook / dashboard
```

## 6. Warehouse Design

DuckDB is used as the local analytical warehouse.

Warehouse file:

```text
db/gdelt_sea.duckdb
```

Main layers:

```text
metadata
raw
staging
marts
```

The raw table is:

```text
raw.gdelt_events
```

This table preserves GDELT event structure but is already scoped to Southeast Asia.

## 7. dbt Transformation Design

dbt is used to separate transformation logic from ingestion logic.

Main dbt layers:

```text
staging.stg_gdelt_events
staging.stg_sea_countries

marts.dim_date
marts.dim_country
marts.dim_event_code
marts.dim_actor
marts.fact_event_signal
```

The star schema supports structured analysis and dashboard outputs.

## 8. Analysis Marts

The project creates three analysis marts:

```text
marts.mart_regional_spike_monitoring
marts.mart_country_event_profile
marts.mart_country_actor_profile
```

These support:

1. regional spike monitoring
2. country event profiling
3. country actor profiling

## 9. Data Quality

dbt tests validate key fields and relationships.

Current expected result:

```text
PASS=60
WARN=0
ERROR=0
TOTAL=60
```

The tests cover:

- not-null checks
- uniqueness checks
- relationship checks between fact and dimension tables

## 10. Notebook and Dashboard

Notebook:

```text
notebooks/block_11_analysis.ipynb
```

Dashboard:

```text
dashboard/app.py
```

The notebook supports analysis review.

The Streamlit dashboard provides a simple local interface for filtering and exploring the marts.

## 11. Optional Extensions

Implemented optional extensions:

```text
Block 13: Spark batch demo
Block 14: one-command orchestration runner
Block 15: local scheduled refresh scaffold
Block 16: architecture and defence documentation
Block 17: final packaging and demo readiness
```

Spark is included only as a local distributed batch-processing demonstration.

The core MVP remains DuckDB and dbt.

## 12. Limitations

Important limitations:

- GDELT is media-coded and noisy.
- Outputs are signals, not verified incident counts.
- Current implementation uses a controlled local sample.
- Spike flag is simple and demonstrative.
- Dashboard is local, not deployed.
- Scheduling is local scaffold, not production orchestration.

## 13. Future Improvements

Possible future improvements:

- run a larger rolling 90-day ingestion
- improve event classification logic
- add richer public-safety taxonomy
- add better actor cleaning
- deploy dashboard
- compare DuckDB workflow with BigQuery
- migrate group collaboration version to BigQuery or another shared warehouse

## 14. Closing Statement

This project demonstrates an end-to-end data engineering workflow:

```text
source discovery
controlled ingestion
local warehouse loading
dbt transformation
data quality tests
analysis marts
notebook analysis
local dashboard
documentation and orchestration
```

The main value is not that it is production-ready. The main value is that it is explainable, reproducible and defensible as a complete data engineering MVP.