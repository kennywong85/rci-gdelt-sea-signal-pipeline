from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt" / "gdelt_sea"


def run_command(
    label: str,
    command: list[str],
    cwd: Path = PROJECT_ROOT,
) -> None:
    """Run a shell command step and stop the pipeline if it fails."""
    print("\n" + "=" * 80)
    print(f"START: {label}")
    print("=" * 80)
    print("Command:", " ".join(command))
    print("Working directory:", cwd)

    start_time = time.time()

    result = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
    )

    elapsed_seconds = round(time.time() - start_time, 2)

    if result.returncode != 0:
        print("\n" + "!" * 80)
        print(f"FAILED: {label}")
        print(f"Exit code: {result.returncode}")
        print(f"Elapsed seconds: {elapsed_seconds}")
        print("!" * 80)
        raise SystemExit(result.returncode)

    print("\n" + "-" * 80)
    print(f"COMPLETED: {label}")
    print(f"Elapsed seconds: {elapsed_seconds}")
    print("-" * 80)


def build_pipeline_steps(args: argparse.Namespace) -> list[tuple[str, list[str], Path]]:
    """Build the ordered list of pipeline commands."""
    python = sys.executable

    steps: list[tuple[str, list[str], Path]] = []

    if args.include_smoke_tests:
        steps.append(
            (
                "GDELT source smoke test",
                [python, "scripts/p02_01_gdelt_source_smoke_test.py"],
                PROJECT_ROOT,
            )
        )

    steps.append(
        (
            "Build rolling GDELT file inventory",
            [
                python,
                "scripts/p02_02_gdelt_90day_inventory.py",
                "--days",
                str(args.days),
            ],
            PROJECT_ROOT,
        )
    )

    steps.append(
        (
            "Build GDELT download manifest",
            [
                python,
                "scripts/p03_01_gdelt_download_manifest.py",
                "--days",
                str(args.days),
            ],
            PROJECT_ROOT,
        )
    )

    if not args.skip_download:
        steps.append(
            (
                "Controlled GDELT download and extraction",
                [
                    python,
                    "scripts/p03_02_gdelt_controlled_downloader.py",
                    "--days",
                    str(args.days),
                    "--max-files",
                    str(args.max_files),
                    "--order",
                    args.order,
                ],
                PROJECT_ROOT,
            )
        )

    if args.include_smoke_tests:
        steps.append(
            (
                "DuckDB SEA filter smoke test",
                [python, "scripts/p04_01_gdelt_sea_filter_test.py"],
                PROJECT_ROOT,
            )
        )

    steps.append(
        (
            "Load raw SEA-filtered GDELT rows into DuckDB",
            [
                python,
                "scripts/p05_01_load_raw_gdelt_to_duckdb.py",
                "--days",
                str(args.days),
            ],
            PROJECT_ROOT,
        )
    )

    if not args.skip_dbt:
        steps.extend(
            [
                (
                    "dbt debug",
                    ["dbt", "debug", "--profiles-dir", "."],
                    DBT_PROJECT_DIR,
                ),
                (
                    "dbt run",
                    ["dbt", "run", "--profiles-dir", "."],
                    DBT_PROJECT_DIR,
                ),
                (
                    "dbt test",
                    ["dbt", "test", "--profiles-dir", "."],
                    DBT_PROJECT_DIR,
                ),
            ]
        )

    return steps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local RCI GDELT SEA signal pipeline."
    )

    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Rolling GDELT file inventory window in days. Default: 90.",
    )

    parser.add_argument(
        "--max-files",
        type=int,
        default=14,
        help="Maximum number of GDELT files to download in this run. Default: 14.",
    )

    parser.add_argument(
        "--order",
        choices=["latest", "oldest"],
        default="latest",
        help="Download ordering for controlled downloader. Default: latest.",
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip controlled download/extraction and use existing local files.",
    )

    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Skip dbt debug/run/test steps.",
    )

    parser.add_argument(
        "--include-smoke-tests",
        action="store_true",
        help="Also run source and SEA filter smoke-test scripts.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("\nRCI GDELT SEA Signal Pipeline Runner")
    print("=" * 80)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"dbt project: {DBT_PROJECT_DIR}")
    print(f"Days: {args.days}")
    print(f"Max files: {args.max_files}")
    print(f"Order: {args.order}")
    print(f"Skip download: {args.skip_download}")
    print(f"Skip dbt: {args.skip_dbt}")
    print(f"Include smoke tests: {args.include_smoke_tests}")

    if not DBT_PROJECT_DIR.exists():
        raise FileNotFoundError(f"dbt project folder not found: {DBT_PROJECT_DIR}")

    steps = build_pipeline_steps(args)

    pipeline_start = time.time()

    for label, command, cwd in steps:
        run_command(label, command, cwd)

    total_elapsed_seconds = round(time.time() - pipeline_start, 2)

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Total elapsed seconds: {total_elapsed_seconds}")
    print("=" * 80)


if __name__ == "__main__":
    main()