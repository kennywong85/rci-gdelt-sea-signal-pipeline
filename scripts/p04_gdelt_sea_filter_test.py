from pathlib import Path
from zipfile import ZipFile
import argparse
import requests
import duckdb

from p02_gdelt_source_smoke_test import GDELT_EVENT_COLUMNS


# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "gdelt_events"
SEA_TEST_DIR = RAW_DIR / "sea_filter_test"
LOOKUP_PATH = PROJECT_ROOT / "data" / "lookup" / "sea_country_codes.csv"

SEA_TEST_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# GDELT source list
# -----------------------------
MASTER_FILE_LIST_URL = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"


def get_latest_gdelt_event_file_urls(number_of_files: int) -> list[str]:
    """Return the latest N GDELT 2.0 Events export zip URLs."""

    print("Fetching GDELT master file list...")

    response = requests.get(MASTER_FILE_LIST_URL, timeout=60)
    response.raise_for_status()

    lines = response.text.strip().splitlines()
    event_file_urls = []

    for line in lines:
        parts = line.split()
        if len(parts) < 3:
            continue

        file_url = parts[-1]

        if file_url.endswith(".export.CSV.zip"):
            event_file_urls.append(file_url)

    if not event_file_urls:
        raise RuntimeError("No GDELT Events export files found.")

    selected_urls = event_file_urls[-number_of_files:]

    print(f"Selected latest {len(selected_urls)} GDELT Events files.")

    return selected_urls


def download_file(url: str, output_dir: Path) -> Path:
    """Download one GDELT zip file if not already present."""

    output_path = output_dir / url.split("/")[-1]

    if output_path.exists():
        print(f"Already downloaded: {output_path.name}")
        return output_path

    print(f"Downloading: {url}")

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    output_path.write_bytes(response.content)

    print(f"Saved: {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")

    return output_path


def unzip_gdelt_file(zip_path: Path, output_dir: Path) -> Path:
    """Unzip one GDELT event file if not already extracted."""

    expected_csv_name = zip_path.name.replace(".zip", "")
    expected_csv_path = output_dir / expected_csv_name

    if expected_csv_path.exists():
        print(f"Already extracted: {expected_csv_path.name}")
        return expected_csv_path

    print(f"Unzipping: {zip_path.name}")

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)
        extracted_names = zip_ref.namelist()

    if not extracted_names:
        raise RuntimeError(f"Zip file was empty: {zip_path}")

    extracted_path = output_dir / extracted_names[0]

    return extracted_path


def download_and_extract_files(number_of_files: int) -> None:
    """Download and extract latest N GDELT event files."""

    urls = get_latest_gdelt_event_file_urls(number_of_files)

    for url in urls:
        zip_path = download_file(url, SEA_TEST_DIR)
        unzip_gdelt_file(zip_path, SEA_TEST_DIR)


def inspect_sea_filter() -> None:
    """Use DuckDB to filter downloaded GDELT files to Southeast Asia."""

    print("\nInspecting downloaded files with DuckDB...")

    csv_glob_path = SEA_TEST_DIR / "*.export.CSV"

    if not list(SEA_TEST_DIR.glob("*.export.CSV")):
        raise RuntimeError("No extracted GDELT CSV files found for SEA filter test.")

    column_defs = ", ".join([f"'{col}': 'VARCHAR'" for col in GDELT_EVENT_COLUMNS])

    con = duckdb.connect()

    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW raw_gdelt AS
        SELECT *
        FROM read_csv(
            '{csv_glob_path}',
            delim = '\t',
            header = false,
            columns = {{{column_defs}}},
            ignore_errors = true
        );
    """)

    con.execute(f"""
        CREATE OR REPLACE TEMP VIEW sea_country_lookup AS
        SELECT *
        FROM read_csv_auto('{LOOKUP_PATH}', header = true);
    """)

    total_rows = con.execute("""
        SELECT COUNT(*) AS total_rows
        FROM raw_gdelt;
    """).fetchone()[0]

    sea_rows = con.execute("""
        SELECT COUNT(*) AS sea_rows
        FROM raw_gdelt r
        INNER JOIN sea_country_lookup c
            ON r.ActionGeo_CountryCode = c.gdelt_fips_code;
    """).fetchone()[0]

    print(f"\nTotal raw GDELT rows inspected: {total_rows:,}")
    print(f"Rows matching SEA ActionGeo country codes: {sea_rows:,}")

    print("\nSEA rows by country:")
    sea_country_counts = con.execute("""
        SELECT
            c.country_name,
            r.ActionGeo_CountryCode,
            COUNT(*) AS event_signal_count,
            MIN(r.SQLDATE) AS earliest_sqldate,
            MAX(r.SQLDATE) AS latest_sqldate
        FROM raw_gdelt r
        INNER JOIN sea_country_lookup c
            ON r.ActionGeo_CountryCode = c.gdelt_fips_code
        GROUP BY
            c.country_name,
            r.ActionGeo_CountryCode
        ORDER BY
            event_signal_count DESC,
            c.country_name;
    """).fetchdf()

    if sea_country_counts.empty:
        print("No SEA rows found in this sample window.")
        print("Try increasing the number of files, e.g. --files 288 for roughly 3 days.")
    else:
        print(sea_country_counts.to_string(index=False))

    print("\nSample SEA event rows:")
    sea_preview = con.execute("""
        SELECT
            r.GLOBALEVENTID,
            r.SQLDATE,
            c.country_name,
            r.ActionGeo_FullName,
            r.ActionGeo_CountryCode,
            r.Actor1Name,
            r.Actor2Name,
            r.EventCode,
            r.EventBaseCode,
            r.EventRootCode,
            r.QuadClass,
            r.NumMentions,
            r.NumSources,
            r.NumArticles,
            r.AvgTone,
            r.SOURCEURL
        FROM raw_gdelt r
        INNER JOIN sea_country_lookup c
            ON r.ActionGeo_CountryCode = c.gdelt_fips_code
        LIMIT 20;
    """).fetchdf()

    if sea_preview.empty:
        print("No sample rows to preview.")
    else:
        print(sea_preview.to_string(index=False))

    print("\nTop non-SEA ActionGeo country codes in the sample:")
    top_non_sea_codes = con.execute("""
        SELECT
            r.ActionGeo_CountryCode,
            COUNT(*) AS row_count
        FROM raw_gdelt r
        LEFT JOIN sea_country_lookup c
            ON r.ActionGeo_CountryCode = c.gdelt_fips_code
        WHERE
            c.gdelt_fips_code IS NULL
            AND r.ActionGeo_CountryCode IS NOT NULL
            AND r.ActionGeo_CountryCode <> ''
        GROUP BY
            r.ActionGeo_CountryCode
        ORDER BY
            row_count DESC
        LIMIT 15;
    """).fetchdf()

    print(top_non_sea_codes.to_string(index=False))

    con.close()

    print("\nProject Block 4: DuckDB SEA filtering prototype completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download recent GDELT event files and test Southeast Asia filtering."
    )

    parser.add_argument(
        "--files",
        type=int,
        default=96,
        help="Number of latest GDELT 15-minute event files to inspect. 96 is roughly 24 hours.",
    )

    args = parser.parse_args()

    download_and_extract_files(args.files)
    inspect_sea_filter()


if __name__ == "__main__":
    main()
