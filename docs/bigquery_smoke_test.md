# BigQuery Public Dataset Smoke Test

This document explains the optional BigQuery smoke test used in Block 18.

## Purpose

The core GDELT project uses DuckDB as the local analytical warehouse.

Block 18 does not migrate the project to BigQuery.

Instead, it demonstrates that the environment can connect to BigQuery and run a small query against a public dataset.

## Script

```text
scripts/p18_01_bigquery_public_smoke_test.py