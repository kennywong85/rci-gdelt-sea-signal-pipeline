from pathlib import Path
import argparse
import pandas as pd

from p02_gdelt_90day_inventory import build_event_file_inventory


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_GDELT_DIR = PROJECT_ROOT / "data" / "raw" / "gdelt_events"
ROLLING_RAW_DIR = RAW_GDELT_DIR / "rolling_90_days"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

ROLLING_RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def build_download_manifest(days: int) -> pd.DataFrame:
    """
    Build a local download manifest for the rolling GDELT file window.

    The manifest compares the expected GDELT files against local files already
    present in data/raw/gdelt_events/rolling_90_days.
    """

    inventory_df = build_event_file_inventory(days=days)

    if inventory_df.empty:
        raise RuntimeError("No GDELT files found in inventory. Cannot build manifest.")

    manifest_df = inventory_df.copy()

    manifest_df["zip_local_path"] = manifest_df["filename"].apply(
        lambda filename: str(ROLLING_RAW_DIR / filename)
    )

    manifest_df["csv_filename"] = manifest_df["filename"].str.replace(
        ".zip",
        "",
        regex=False,
    )

    manifest_df["csv_local_path"] = manifest_df["csv_filename"].apply(
        lambda filename: str(ROLLING_RAW_DIR / filename)
    )

    manifest_df["zip_exists"] = manifest_df["zip_local_path"].apply(
        lambda path: Path(path).exists()
    )

    manifest_df["csv_exists"] = manifest_df["csv_local_path"].apply(
        lambda path: Path(path).exists()
    )

    manifest_df["needs_download"] = ~manifest_df["zip_exists"]
    manifest_df["needs_extract"] = manifest_df["zip_exists"] & ~manifest_df["csv_exists"]

    manifest_df["local_status"] = "missing"

    manifest_df.loc[
        manifest_df["zip_exists"] & ~manifest_df["csv_exists"],
        "local_status",
    ] = "zip_downloaded_not_extracted"

    manifest_df.loc[
        manifest_df["zip_exists"] & manifest_df["csv_exists"],
        "local_status",
    ] = "ready"

    manifest_df["manifest_generated_at_utc"] = pd.Timestamp.utcnow()

    return manifest_df


def print_manifest_summary(manifest_df: pd.DataFrame, days: int) -> None:
    """Print summary statistics for the download manifest."""

    print("\nGDELT download manifest summary")
    print("--------------------------------")

    print(f"Rolling window requested: {days} days")
    print(f"Files expected: {len(manifest_df):,}")

    status_counts = (
        manifest_df["local_status"]
        .value_counts()
        .rename_axis("local_status")
        .reset_index(name="file_count")
    )

    print("\nLocal file status:")
    print(status_counts.to_string(index=False))

    files_needing_download = int(manifest_df["needs_download"].sum())
    files_needing_extract = int(manifest_df["needs_extract"].sum())
    files_ready = int((manifest_df["local_status"] == "ready").sum())

    print(f"\nFiles needing download: {files_needing_download:,}")
    print(f"Files needing extraction: {files_needing_extract:,}")
    print(f"Files ready for loading: {files_ready:,}")

    print("\nLatest 5 expected files:")
    latest_files = manifest_df[
        [
            "file_datetime_utc",
            "filename",
            "local_status",
            "needs_download",
            "needs_extract",
        ]
    ].tail()

    print(latest_files.to_string(index=False))

    print("\nFirst 5 files needing download:")
    download_preview = manifest_df.loc[
        manifest_df["needs_download"],
        ["file_datetime_utc", "filename", "file_url"],
    ].head()

    if download_preview.empty:
        print("No files need downloading.")
    else:
        print(download_preview.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a GDELT rolling-window download manifest."
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Rolling number of days to include. Default: 90.",
    )

    args = parser.parse_args()

    manifest_df = build_download_manifest(days=args.days)

    output_path = PROCESSED_DIR / f"gdelt_download_manifest_{args.days}_days.csv"
    manifest_df.to_csv(output_path, index=False)

    print_manifest_summary(manifest_df, days=args.days)

    print(f"\nManifest saved to: {output_path}")
    print("\nBlock 4 GDELT download manifest completed successfully.")


if __name__ == "__main__":
    main()
