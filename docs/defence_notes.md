# Defence Notes

This document summarises how to explain the project in class.

## One-Sentence Project Summary

This project builds a local data engineering pipeline that ingests GDELT 2.0 Events data, filters for Southeast Asia public-safety-related event signals, transforms the data into tested dbt marts, and presents the results through a notebook and local Streamlit dashboard.

## Core Question

How can public-safety stakeholders monitor evolving conflict and disorder signals across Southeast Asia using regularly refreshed open news-event data?

## What GDELT Represents

GDELT is treated as a media-coded event signal source.

It should not be presented as a verified ground-truth incident database.

Use cautious language:

- media-coded events
- event signals
- signal volume
- public-safety-related indicators
- areas for further investigation

Avoid overclaiming:

- confirmed incidents
- true conflict counts
- verified security events

## Why DuckDB

DuckDB is used as the local analytical warehouse.

It is appropriate for the individual MVP because it is:

- lightweight
- local
- reproducible
- SQL-friendly
- compatible with dbt through `dbt-duckdb`

For group collaboration, a shared warehouse such as BigQuery may be more suitable.

## Why dbt

dbt separates transformation logic from ingestion logic.

Python handles:

- source discovery
- download manifest
- controlled downloader
- raw DuckDB load
- local orchestration

dbt handles:

- staging models
- star schema
- analysis marts
- tests
- source/model documentation

## Why Spark Is Optional

Spark is included only as a distributed batch-processing demonstration.

The core MVP does not require Spark because the controlled local sample is small and DuckDB is sufficient.

Spark demonstrates that the raw-file pattern can be processed using distributed batch concepts if scale increases.

## Why Kafka Is Not Used

Kafka is more suitable for streaming/event-driven architectures.

This project is a batch file-ingestion pipeline:

```text
discover files → download files → load warehouse → transform/test → analyse/dashboard
```

Therefore Kafka is not required for the MVP.

## Why Meltano Is Not Used

Meltano is useful for connector-based ELT from APIs or SaaS systems.

This project uses GDELT public file lists and ZIP/CSV event files, so a custom Python ingestion layer is more direct and easier to explain.

## Key Limitations

- The current MVP uses a controlled local sample, not necessarily the full 90-day universe.
- GDELT is media-coded and noisy.
- Actor labels can be inconsistent or ambiguous.
- The spike flag is a simple demonstration rule, not a production alerting model.
- The dashboard is local and not deployed.
- The pipeline prioritises learning, reproducibility and explainability over production hardening.

## Defence Framing

The strongest way to explain the project:

1. I built a file-based batch ingestion pipeline from GDELT.
2. I used DuckDB as a local analytical warehouse.
3. I used dbt to create clean, tested transformation layers.
4. I created analysis marts aligned to two stakeholder use cases.
5. I demonstrated outputs through a notebook and local dashboard.
6. I added optional Spark and local orchestration/refresh blocks as learning extensions.
7. I kept the design explainable and avoided unnecessary production complexity.

## Short Defence Script

The project follows an ELT pattern. Python discovers and downloads GDELT event files, then loads Southeast Asia-filtered event rows into DuckDB. dbt transforms the raw data into staging models, a star schema and analysis marts, with tests for key fields and relationships. The notebook and dashboard read from the marts to support regional spike monitoring and country-level event/actor profiling. Spark and local scheduling are included as optional demonstrations, while the core MVP remains DuckDB and dbt for simplicity and reproducibility.