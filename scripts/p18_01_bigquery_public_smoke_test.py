from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "bigquery_public_smoke_test.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a small BigQuery public dataset smoke test."
    )
    parser.add_argument(
        "--project-id",
        default=os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"),
        help="Google Cloud project ID to bill/query from.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="CSV output path for smoke test result.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.project_id:
        raise ValueError(
            "No project ID provided. Use --project-id or set GOOGLE_CLOUD_PROJECT."
        )

    try:
        from google.cloud import bigquery
    except Exception as exc:
        raise ImportError(
            "google-cloud-bigquery is not installed. "
            "Install it with: python -m pip install google-cloud-bigquery"
        ) from exc

    query = """
    SELECT
      corpus,
      SUM(word_count) AS total_word_count
    FROM `bigquery-public-data.samples.shakespeare`
    GROUP BY corpus
    ORDER BY total_word_count DESC
    LIMIT 10
    """

    print("Running BigQuery public dataset smoke test...")
    print(f"Project ID: {args.project_id}")

    client = bigquery.Client(project=args.project_id)
    rows = list(client.query(query).result())

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["corpus", "total_word_count"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "corpus": row["corpus"],
                    "total_word_count": row["total_word_count"],
                }
            )

    print("\nBigQuery smoke test result:")
    for row in rows:
        print(f"{row['corpus']}: {row['total_word_count']}")

    print(f"\nSaved output to: {output_path}")
    print("BigQuery public dataset smoke test completed successfully.")


if __name__ == "__main__":
    main()