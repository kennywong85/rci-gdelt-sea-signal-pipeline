from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import re
import requests
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FILE_LIST_URL = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"

GDELT_EVENT_FILE_PATTERN = re.compile(r"(\d{14})\.export\.CSV\.zip$")


def parse_gdelt_timestamp_from_url(file_url: str) -> datetime | None:
    """
    Extract datetime from a GDELT 2.0 Events filename.

    Example:
    20260521151500.export.CSV.zip
    means 2026-05-21 15:15:00 UTC.
    """

    filename = file_url.split("/")[-1]
    match = GDELT_EVENT_FILE_PATTERN.search(filename)

    if not match:
        return None

    timestamp_text = match.group(1)

    return datetime.strptime(timestamp_text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def safe_int(value: str) -> int | None:
    """
    Convert a value to int only if it is actually numeric.

    Some GDELT master file list fields may contain hashes or metadata,
    so we do not blindly int() everything like an overconfident intern.
    """

    if value.isdigit():
        return int(value)

    return None


def fetch_master_file_list() -> list[str]:
    """Fetch the GDELT 2.0 master file list and return raw text lines."""

    print("Fetching GDELT master file list...")

    response = requests.get(MASTER_FILE_LIST_URL, timeout=60)
    response.raise_for_status()

    return response.text.strip().splitlines()


def build_event_file_inventory(days: int) -> pd.DataFrame:
    """Build a file inventory for GDELT 2.0 Events files within the rolling window."""

    lines = fetch_master_file_list()

    now_utc = datetime.now(timezone.utc)
    window_start = now_utc - timedelta(days=days)

    records = []

    for line in lines:
        parts = line.split()

        if len(parts) < 1:
            continue

        file_url = parts[-1]

        if not file_url.endswith(".export.CSV.zip"):
            continue

        file_datetime_utc = parse_gdelt_timestamp_from_url(file_url)

        if file_datetime_utc is None:
            continue

        if file_datetime_utc < window_start:
            continue

        filename = file_url.split("/")[-1]

        # Best-effort size parsing.
        # We do not rely on these fields because the master list can contain non-numeric metadata.
        possible_size_1 = safe_int(parts[0]) if len(parts) >= 1 else None
        possible_size_2 = safe_int(parts[1]) if len(parts) >= 2 else None

        records.append(
            {
                "file_datetime_utc": file_datetime_utc,
                "file_date": file_datetime_utc.date().isoformat(),
                "file_hour": file_datetime_utc.hour,
                "file_minute": file_datetime_utc.minute,
                "filename": filename,
                "file_url": file_url,
                "size_field_1_bytes": possible_size_1,
                "size_field_2_bytes": possible_size_2,
            }
        )

    inventory_df = pd.DataFrame(records)

    if inventory_df.empty:
        return inventory_df

    inventory_df = inventory_df.sort_values("file_datetime_utc").reset_index(drop=True)

    # Convert optional size fields into numeric values.
    # Some master file list rows contain non-numeric metadata, so we coerce bad values to NaN.
    inventory_df["size_field_1_bytes"] = pd.to_numeric(
        inventory_df["size_field_1_bytes"],
        errors="coerce",
    )

    inventory_df["size_field_2_bytes"] = pd.to_numeric(
        inventory_df["size_field_2_bytes"],
        errors="coerce",
    )

    inventory_df["size_field_1_mb"] = (
        inventory_df["size_field_1_bytes"] / 1024 / 1024
    ).round(2)

    inventory_df["size_field_2_mb"] = (
        inventory_df["size_field_2_bytes"] / 1024 / 1024
    ).round(2)

    return inventory_df


def print_inventory_summary(inventory_df: pd.DataFrame, days: int) -> None:
    """Print useful summary statistics for the inventory."""

    print("\nGDELT rolling inventory summary")
    print("--------------------------------")

    if inventory_df.empty:
        print("No files found in the selected window.")
        return

    print(f"Rolling window requested: {days} days")
    print(f"Files found: {len(inventory_df):,}")
    print(f"Earliest file: {inventory_df['file_datetime_utc'].min()}")
    print(f"Latest file:   {inventory_df['file_datetime_utc'].max()}")

    files_by_date = (
        inventory_df.groupby("file_date")
        .size()
        .reset_index(name="file_count")
        .sort_values("file_date")
    )

    print("\nFirst 5 dates in inventory:")
    print(files_by_date.head().to_string(index=False))

    print("\nLast 5 dates in inventory:")
    print(files_by_date.tail().to_string(index=False))

    print("\nLatest 5 files:")
    latest_files = inventory_df[
        ["file_datetime_utc", "filename", "file_url"]
    ].tail()

    print(latest_files.to_string(index=False))

    if inventory_df["size_field_1_bytes"].notna().any():
        total_size_1_mb = inventory_df["size_field_1_mb"].sum()
        print(f"\nEstimated total size field 1: {total_size_1_mb:,.2f} MB")

    if inventory_df["size_field_2_bytes"].notna().any():
        total_size_2_mb = inventory_df["size_field_2_mb"].sum()
        print(f"Estimated total size field 2: {total_size_2_mb:,.2f} MB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a rolling GDELT 2.0 Events file inventory."
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Rolling number of days to include in inventory. Default: 90.",
    )

    args = parser.parse_args()

    inventory_df = build_event_file_inventory(days=args.days)

    output_path = PROCESSED_DIR / f"gdelt_event_file_inventory_{args.days}_days.csv"
    inventory_df.to_csv(output_path, index=False)

    print_inventory_summary(inventory_df, days=args.days)

    print(f"\nInventory saved to: {output_path}")
    print("\nProject Block 2: GDELT rolling inventory completed successfully.")


if __name__ == "__main__":
    main()
