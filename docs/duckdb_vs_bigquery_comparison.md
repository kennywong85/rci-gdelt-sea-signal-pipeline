# DuckDB vs BigQuery Comparison Notes

This document compares DuckDB and BigQuery in the context of this individual GDELT project.

## Summary

The individual GDELT project uses DuckDB as the local analytical warehouse.

BigQuery is considered as an optional cloud warehouse comparison, not the core implementation.

The final position for this project is:

```text
DuckDB = core local warehouse for the individual MVP
BigQuery = optional cloud warehouse smoke test / comparison point
```

## DuckDB

DuckDB is a local analytical database.

In this project, DuckDB is used through:

```text
db/gdelt_sea.duckdb
```

This DuckDB file acts as the local data warehouse for the individual prototype.

### Strengths

DuckDB is suitable for this individual project because it is:

- simple to set up locally
- lightweight
- free to run without cloud cost
- good for analytical SQL
- easy to connect to Python
- compatible with dbt through `dbt-duckdb`
- easy to reproduce on one machine
- suitable for controlled local MVP development

DuckDB is especially useful when the goal is to learn and demonstrate:

- file-based ingestion
- local warehouse loading
- SQL transformation
- dbt modelling
- dbt testing
- notebook analysis
- local dashboarding

### Weaknesses

DuckDB is less suitable when multiple users need to work on the same warehouse at the same time.

Limitations include:

- the database is a local file
- collaboration can become awkward
- teammates may end up with different local warehouse states
- it is not a managed cloud warehouse
- it is not ideal as a shared team source of truth
- deployment and access control are not built in like a cloud platform

For a solo individual project, these weaknesses are acceptable.

For a group project, these weaknesses matter more.

## BigQuery

BigQuery is a managed cloud data warehouse provided by Google Cloud.

It is designed for scalable cloud-based querying and shared access.

### Strengths

BigQuery is useful for:

- group collaboration
- shared warehouse access
- scalable query processing
- querying larger datasets
- managed cloud storage and compute
- avoiding local database file sharing
- integration with cloud dashboards and cloud workflows

For a group project, BigQuery can be easier because everyone queries the same shared tables instead of passing around local files.

### Weaknesses

BigQuery also adds complexity.

Potential drawbacks include:

- requires Google Cloud project setup
- may require billing configuration
- can create cost-control concerns
- requires cloud credentials and permissions
- can be more complex than needed for a solo MVP
- may distract from the core learning objective if introduced too early

For this individual project, using BigQuery as the main warehouse would add more cloud setup without much additional learning value.

## Why DuckDB Was Used for the Individual Project

DuckDB was selected because this project is an individual learning MVP.

The main goals were to:

- understand public data source discovery
- build a file-based batch ingestion flow
- create a raw landing zone
- load data into a local analytical warehouse
- practise SQL transformation using dbt
- build staging models, a star schema and analysis marts
- run dbt tests
- analyse outputs in Jupyter
- present outputs in a local Streamlit dashboard

For those goals, DuckDB is sufficient and appropriate.

It keeps the project:

- local
- reproducible
- explainable
- low-cost
- easier to debug
- easier to defend

The project does not need a managed cloud warehouse to prove the core data engineering workflow.

## Why BigQuery May Be Better for a Group Project

BigQuery may be more suitable for a group project because collaboration becomes easier when everyone works from the same warehouse.

In a group setting, BigQuery can help avoid problems such as:

- different people having different local DuckDB files
- database files being too large to share
- uncertainty over whose local copy is correct
- difficulty coordinating dashboard or analysis work
- messy manual syncing of generated outputs

A BigQuery-first group architecture can provide one shared source of truth.

This is especially useful if:

- several people are writing queries
- several people are building dashboards
- the group needs shared validation
- the dataset is large
- the final output needs to be accessed from multiple machines

## Why BigQuery Was Not Added to the Core GDELT Pipeline

The core GDELT pipeline already works with:

```text
GDELT files
→ local raw files
→ DuckDB
→ dbt
→ notebook/dashboard
```

Adding BigQuery to the core pipeline would require additional design decisions, such as:

- where to stage raw files
- how to load GDELT CSV data into BigQuery
- how to manage credentials
- how to manage datasets and table naming
- how to control query costs
- whether dbt should target DuckDB or BigQuery
- whether the dashboard should read from DuckDB or BigQuery

Those decisions are useful for a production or group architecture, but they are not necessary for this individual MVP.

Therefore, BigQuery is kept as an optional smoke test and comparison point.

## What Block 18 Demonstrates

Block 18 demonstrates that the environment can connect to BigQuery and query a public dataset.

The script is:

```text
scripts/p18_01_bigquery_public_smoke_test.py
```

The documentation is:

```text
docs/bigquery_smoke_test.md
```

The smoke test does not migrate the GDELT pipeline to BigQuery.

It simply proves basic BigQuery query capability.

## Final Position

For this individual GDELT MVP:

```text
DuckDB = core local analytical warehouse
BigQuery = optional cloud query smoke test and comparison note
```

For a collaborative group project:

```text
BigQuery or another shared cloud warehouse may be preferred
```

The key point is that neither tool is universally better.

The better choice depends on:

- project size
- collaboration needs
- deployment needs
- cost constraints
- cloud access
- reproducibility needs
- learning objectives

For this project, DuckDB is the right core choice because it supports a clean, local, explainable data engineering MVP.

BigQuery is useful to understand and mention, but not necessary to the core individual implementation.