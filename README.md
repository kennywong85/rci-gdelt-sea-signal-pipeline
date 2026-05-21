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

lock 0: Project setup and repo skeleton

Status: Completed.

