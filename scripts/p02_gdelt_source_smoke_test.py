from pathlib import Path
from zipfile import ZipFile
import requests
import duckdb


# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "gdelt_events"
SMOKE_DIR = RAW_DIR / "smoke_test"

SMOKE_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# GDELT source list
# -----------------------------
MASTER_FILE_LIST_URL = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"


# -----------------------------
# GDELT 2.0 Events column names
# Source files are tab-delimited, no header row.
# -----------------------------
GDELT_EVENT_COLUMNS = [
    "GLOBALEVENTID",
    "SQLDATE",
    "MonthYear",
    "Year",
    "FractionDate",
    "Actor1Code",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor1KnownGroupCode",
    "Actor1EthnicCode",
    "Actor1Religion1Code",
    "Actor1Religion2Code",
    "Actor1Type1Code",
    "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code",
    "Actor2Name",
    "Actor2CountryCode",
    "Actor2KnownGroupCode",
    "Actor2EthnicCode",
    "Actor2Religion1Code",
    "Actor2Religion2Code",
    "Actor2Type1Code",
    "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "QuadClass",
    "GoldsteinScale",
    "NumMentions",
    "NumSources",
    "NumArticles",
    "AvgTone",
    "Actor1Geo_Type",
    "Actor1Geo_FullName",
    "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code",
    "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat",
    "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type",
    "Actor2Geo_FullName",
    "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code",
    "Actor2Geo_ADM2Code",
    "Actor2Geo_Lat",
    "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code",
    "ActionGeo_ADM2Code",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED",
    "SOURCEURL",
]


def get_latest_gdelt_event_file_url() -> str:
    """Read GDELT master file list and return the latest 2.0 Events export zip URL."""

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
        raise RuntimeError("No GDELT Events export files found in master file list.")

    latest_url = event_file_urls[-1]
    print(f"Latest GDELT Events file found: {latest_url}")

    return latest_url


def download_file(url: str, output_dir: Path) -> Path:
    """Download a file if it does not already exist locally."""

    output_path = output_dir / url.split("/")[-1]

    if output_path.exists():
        print(f"File already exists, skipping download: {output_path}")
        return output_path

    print(f"Downloading: {url}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    output_path.write_bytes(response.content)

    print(f"Saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

    return output_path


def unzip_gdelt_file(zip_path: Path, output_dir: Path) -> Path:
    """Unzip the GDELT CSV file."""

    print(f"Unzipping: {zip_path}")

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)
        extracted_names = zip_ref.namelist()

    if not extracted_names:
        raise RuntimeError("Zip file was empty.")

    extracted_path = output_dir / extracted_names[0]

    print(f"Extracted CSV: {extracted_path}")

    return extracted_path


def inspect_with_duckdb(csv_path: Path) -> None:
    """Use DuckDB to inspect the extracted GDELT CSV file."""

    print("\nInspecting file with DuckDB...")

    column_defs = ", ".join([f"'{col}': 'VARCHAR'" for col in GDELT_EVENT_COLUMNS])

    con = duckdb.connect()

    row_count_query = f"""
        SELECT COUNT(*) AS row_count
        FROM read_csv(
            '{csv_path}',
            delim = '\t',
            header = false,
            columns = {{{column_defs}}},
            ignore_errors = true
        );
    """

    preview_query = f"""
        SELECT
            GLOBALEVENTID,
            SQLDATE,
            Actor1Name,
            Actor2Name,
            EventCode,
            EventBaseCode,
            EventRootCode,
            QuadClass,
            ActionGeo_FullName,
            ActionGeo_CountryCode,
            NumMentions,
            NumSources,
            NumArticles,
            AvgTone,
            DATEADDED,
            SOURCEURL
        FROM read_csv(
            '{csv_path}',
            delim = '\t',
            header = false,
            columns = {{{column_defs}}},
            ignore_errors = true
        )
        LIMIT 10;
    """

    row_count = con.execute(row_count_query).fetchone()[0]
    preview_df = con.execute(preview_query).fetchdf()

    print(f"\nTotal rows in this GDELT file: {row_count:,}")
    print("\nPreview:")
    print(preview_df.to_string(index=False))

    con.close()


def main() -> None:
    latest_url = get_latest_gdelt_event_file_url()
    zip_path = download_file(latest_url, SMOKE_DIR)
    csv_path = unzip_gdelt_file(zip_path, SMOKE_DIR)
    inspect_with_duckdb(csv_path)

    print("\nProject Block 2: GDELT source smoke test completed successfully.")


if __name__ == "__main__":
    main()
