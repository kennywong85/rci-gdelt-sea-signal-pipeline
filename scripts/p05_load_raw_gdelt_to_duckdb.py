from pathlib import Path
import argparse
import duckdb

from p02_gdelt_source_smoke_test import GDELT_EVENT_COLUMNS
from p03_gdelt_download_manifest import build_download_manifest, ROLLING_RAW_DIR


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "gdelt_sea.duckdb"
LOOKUP_PATH = PROJECT_ROOT / "data" / "lookup" / "sea_country_codes.csv"


def get_ready_csv_files(days: int) -> list[Path]:
    """
    Use the download manifest to identify ready CSV files.

    A file is ready when both its ZIP and extracted CSV exist locally.
    """

    manifest_df = build_download_manifest(days=days)

    ready_df = manifest_df.loc[manifest_df["local_status"] == "ready"].copy()

    ready_csv_paths = [Path(path) for path in ready_df["csv_local_path"].tolist()]

    return ready_csv_paths


def build_column_definitions() -> str:
    """
    Build DuckDB read_csv column definitions.

    GDELT files do not have a header row, so we manually provide column names.
    Everything is loaded as VARCHAR at raw layer.
    """

    return ", ".join([f"'{column_name}': 'VARCHAR'" for column_name in GDELT_EVENT_COLUMNS])


def load_ready_files_to_raw_table(days: int) -> None:
    """Load ready GDELT CSV files into DuckDB raw.gdelt_events."""

    ready_csv_files = get_ready_csv_files(days=days)

    print("\nBlock 6 raw load plan")
    print("---------------------")
    print(f"Rolling window: {days} days")
    print(f"Ready CSV files found: {len(ready_csv_files):,}")
    print(f"DuckDB path: {DB_PATH}")

    if not ready_csv_files:
        raise RuntimeError(
            "No ready CSV files found. Run Block 5 downloader first."
        )

    csv_glob_path = ROLLING_RAW_DIR / "*.export.CSV"
    column_defs = build_column_definitions()

    con = duckdb.connect(str(DB_PATH))

    print("\nCreating schemas...")
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    con.execute("CREATE SCHEMA IF NOT EXISTS metadata;")

    print("Registering SEA country lookup...")
    con.execute(f"""
        CREATE OR REPLACE TABLE metadata.sea_country_lookup AS
        SELECT
            country_name,
            gdelt_fips_code,
            notes
        FROM read_csv_auto('{LOOKUP_PATH}', header = true);
    """)

    print("Reading ready GDELT CSV files with DuckDB...")

    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW temp_gdelt_all AS
        SELECT *
        FROM read_csv(
            '{csv_glob_path}',
            delim = '\t',
            header = false,
            columns = {{{column_defs}}},
            ignore_errors = true,
            filename = true
        );
    """)

    total_rows_in_ready_files = con.execute("""
        SELECT COUNT(*) AS row_count
        FROM temp_gdelt_all;
    """).fetchone()[0]

    print(f"Total rows across ready CSV files: {total_rows_in_ready_files:,}")

    print("Creating raw.gdelt_events with SEA-filtered rows...")

    con.execute("""
        CREATE OR REPLACE TABLE raw.gdelt_events AS
        SELECT
            r.*,
            c.country_name AS sea_country_name,
            current_timestamp AS loaded_at_utc
        FROM temp_gdelt_all r
        INNER JOIN metadata.sea_country_lookup c
            ON r.ActionGeo_CountryCode = c.gdelt_fips_code;
    """)

    sea_rows_loaded = con.execute("""
        SELECT COUNT(*) AS row_count
        FROM raw.gdelt_events;
    """).fetchone()[0]

    print(f"SEA rows loaded into raw.gdelt_events: {sea_rows_loaded:,}")

    print("\nSEA rows by country:")
    country_counts = con.execute("""
        SELECT
            sea_country_name,
            ActionGeo_CountryCode,
            COUNT(*) AS event_signal_count,
            MIN(SQLDATE) AS earliest_sqldate,
            MAX(SQLDATE) AS latest_sqldate
        FROM raw.gdelt_events
        GROUP BY
            sea_country_name,
            ActionGeo_CountryCode
        ORDER BY
            event_signal_count DESC,
            sea_country_name;
    """).fetchdf()

    if country_counts.empty:
        print("No SEA rows were loaded. This may happen if the ready file sample is too small.")
        print("Run Block 5 again with more files, then rerun Block 6.")
    else:
        print(country_counts.to_string(index=False))

    print("\nRaw table preview:")
    preview_df = con.execute("""
        SELECT
            GLOBALEVENTID,
            SQLDATE,
            sea_country_name,
            ActionGeo_FullName,
            ActionGeo_CountryCode,
            Actor1Name,
            Actor2Name,
            EventCode,
            EventBaseCode,
            EventRootCode,
            QuadClass,
            NumMentions,
            NumSources,
            NumArticles,
            AvgTone,
            SOURCEURL
        FROM raw.gdelt_events
        LIMIT 20;
    """).fetchdf()

    if preview_df.empty:
        print("No rows to preview.")
    else:
        print(preview_df.to_string(index=False))

    print("\nDuckDB tables created:")
    tables_df = con.execute("""
        SELECT
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema IN ('raw', 'metadata')
        ORDER BY
            table_schema,
            table_name;
    """).fetchdf()

    print(tables_df.to_string(index=False))

    con.close()

    print("\nBlock 6 raw DuckDB load completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load ready GDELT CSV files into DuckDB raw table."
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Rolling number of days to include. Default: 90.",
    )

    args = parser.parse_args()

    load_ready_files_to_raw_table(days=args.days)


if __name__ == "__main__":
    main()
