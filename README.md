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

Block 0: Project scaffold and environment setup.
