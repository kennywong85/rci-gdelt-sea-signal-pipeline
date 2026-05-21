from pathlib import Path
from zipfile import ZipFile, BadZipFile
import argparse
import time
import requests
import pandas as pd

from p03_01_gdelt_download_manifest import build_download_manifest, ROLLING_RAW_DIR


def download_one_file(file_url: str, output_path: Path, timeout: int = 120) -> bool:
    """
    Download one file from GDELT.

    Returns True if download succeeded or file already exists.
    Returns False if download failed.
    """

    if output_path.exists():
        print(f"Already downloaded: {output_path.name}")
        return True

    print(f"Downloading: {output_path.name}")

    try:
        response = requests.get(file_url, timeout=timeout)
        response.raise_for_status()
        output_path.write_bytes(response.content)

        print(f"Saved: {output_path.name} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")
        return True

    except requests.RequestException as error:
        print(f"Download failed for {output_path.name}: {error}")
        return False


def extract_one_zip(zip_path: Path, output_dir: Path) -> bool:
    """
    Extract one GDELT zip file.

    Returns True if extraction succeeded or CSV already exists.
    Returns False if extraction failed.
    """

    csv_path = output_dir / zip_path.name.replace(".zip", "")

    if csv_path.exists():
        print(f"Already extracted: {csv_path.name}")
        return True

    print(f"Extracting: {zip_path.name}")

    try:
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)

        if csv_path.exists():
            print(f"Extracted: {csv_path.name}")
            return True

        print(f"Extraction completed but expected CSV not found: {csv_path.name}")
        return False

    except BadZipFile:
        print(f"Bad zip file, cannot extract: {zip_path.name}")
        return False


def select_files_to_download(
    manifest_df: pd.DataFrame,
    max_files: int,
    order: str,
) -> pd.DataFrame:
    """
    Select missing files from the manifest.

    order='oldest' downloads from the start of the rolling window.
    order='latest' downloads the most recent files first.
    """

    missing_df = manifest_df.loc[manifest_df["needs_download"]].copy()

    if missing_df.empty:
        return missing_df

    ascending = order == "oldest"

    missing_df = missing_df.sort_values(
        "file_datetime_utc",
        ascending=ascending,
    )

    return missing_df.head(max_files)


def run_controlled_download(
    days: int,
    max_files: int,
    order: str,
    sleep_seconds: float,
) -> None:
    """
    Build manifest, download selected missing files, extract them,
    then print refreshed manifest status.
    """

    print("Building download manifest...")
    manifest_df = build_download_manifest(days=days)

    selected_df = select_files_to_download(
        manifest_df=manifest_df,
        max_files=max_files,
        order=order,
    )

    print("\nControlled download plan")
    print("------------------------")
    print(f"Rolling window: {days} days")
    print(f"Missing files available: {int(manifest_df['needs_download'].sum()):,}")
    print(f"Max files to download this run: {max_files}")
    print(f"Download order: {order}")
    print(f"Files selected this run: {len(selected_df):,}")

    if selected_df.empty:
        print("\nNo missing files to download. Nothing to do.")
        return

    print("\nSelected files:")
    print(
        selected_df[
            ["file_datetime_utc", "filename", "file_url"]
        ].to_string(index=False)
    )

    successful_downloads = 0
    successful_extractions = 0

    for row in selected_df.itertuples(index=False):
        file_url = row.file_url
        filename = row.filename
        zip_path = ROLLING_RAW_DIR / filename

        downloaded = download_one_file(file_url=file_url, output_path=zip_path)

        if downloaded:
            successful_downloads += 1

            extracted = extract_one_zip(zip_path=zip_path, output_dir=ROLLING_RAW_DIR)

            if extracted:
                successful_extractions += 1

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    print("\nDownload run summary")
    print("--------------------")
    print(f"Files selected: {len(selected_df):,}")
    print(f"Successful downloads: {successful_downloads:,}")
    print(f"Successful extractions: {successful_extractions:,}")

    failed_downloads = len(selected_df) - successful_downloads
    failed_extractions = successful_downloads - successful_extractions

    if failed_downloads > 0 or failed_extractions > 0:
        print("\nWARNING: Partial success detected.")
        print(f"Failed downloads: {failed_downloads:,}")
        print(f"Failed extractions: {failed_extractions:,}")
        print("This can happen with very recent GDELT files. Re-run the downloader to top up missing files.")
    else:
        print("\nAll selected files downloaded and extracted successfully.")

    print("\nRefreshing manifest after download...")
    refreshed_manifest_df = build_download_manifest(days=days)

    status_counts = (
        refreshed_manifest_df["local_status"]
        .value_counts()
        .rename_axis("local_status")
        .reset_index(name="file_count")
    )

    print("\nUpdated local file status:")
    print(status_counts.to_string(index=False))

    print("\nProject Block 3: controlled GDELT downloader completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Controlled downloader for missing GDELT rolling-window files."
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Rolling number of days to include. Default: 90.",
    )

    parser.add_argument(
        "--max-files",
        type=int,
        default=10,
        help="Maximum number of missing files to download in this run. Default: 10.",
    )

    parser.add_argument(
        "--order",
        choices=["oldest", "latest"],
        default="latest",
        help="Download oldest or latest missing files first. Default: latest.",
    )

    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.25,
        help="Pause between downloads to avoid hammering the source. Default: 0.25.",
    )

    args = parser.parse_args()

    run_controlled_download(
        days=args.days,
        max_files=args.max_files,
        order=args.order,
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    main()
