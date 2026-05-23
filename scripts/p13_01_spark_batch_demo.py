from pathlib import Path
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    broadcast,
    col,
    count,
    sum as spark_sum,
    to_date,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

RAW_CANDIDATE_DIRS = [
    PROJECT_ROOT / "data" / "raw" / "gdelt_events" / "rolling_90_days",
    PROJECT_ROOT / "data" / "raw" / "gdelt_events",
]

LOOKUP_PATH = PROJECT_ROOT / "data" / "lookup" / "sea_country_codes.csv"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "spark_sea_country_summary.csv"

sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from p02_01_gdelt_source_smoke_test import GDELT_EVENT_COLUMNS
except ImportError as exc:
    raise ImportError(
        "Could not import GDELT_EVENT_COLUMNS from "
        "scripts/p02_01_gdelt_source_smoke_test.py"
    ) from exc


def find_raw_gdelt_files() -> list[Path]:
    csv_files: list[Path] = []

    for raw_dir in RAW_CANDIDATE_DIRS:
        if raw_dir.exists():
            csv_files.extend(sorted(raw_dir.rglob("*.export.CSV")))

    unique_files = sorted(set(csv_files))

    if not unique_files:
        searched = "\n".join(str(path) for path in RAW_CANDIDATE_DIRS)
        raise FileNotFoundError(
            "No extracted GDELT CSV files found. Searched:\n"
            f"{searched}\n\n"
            "Run the controlled downloader first."
        )

    return unique_files


def main() -> None:
    csv_files = find_raw_gdelt_files()

    # Keep this demo intentionally small and controlled.
    demo_files = csv_files[:5]

    print("Project root:", PROJECT_ROOT)
    print(f"Raw files available: {len(csv_files)}")
    print(f"Spark demo files used: {len(demo_files)}")

    if not LOOKUP_PATH.exists():
        raise FileNotFoundError(f"SEA country lookup not found: {LOOKUP_PATH}")

    spark = (
        SparkSession.builder
        .appName("rci-gdelt-sea-spark-demo")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    gdelt_df = (
        spark.read
        .option("sep", "\t")
        .option("header", "false")
        .option("inferSchema", "false")
        .csv([str(path) for path in demo_files])
    )

    gdelt_df = gdelt_df.toDF(*GDELT_EVENT_COLUMNS)

    sea_lookup_df = (
        spark.read
        .option("header", "true")
        .csv(str(LOOKUP_PATH))
    )

    sea_events_df = (
        gdelt_df
        .join(
            broadcast(sea_lookup_df),
            gdelt_df["ActionGeo_CountryCode"] == sea_lookup_df["gdelt_fips_code"],
            "inner",
        )
        .withColumn("event_date", to_date(col("SQLDATE").cast("string"), "yyyyMMdd"))
        .withColumn("num_mentions", col("NumMentions").cast("int"))
        .withColumn("num_sources", col("NumSources").cast("int"))
        .withColumn("num_articles", col("NumArticles").cast("int"))
        .withColumn("avg_tone", col("AvgTone").cast("double"))
    )

    summary_df = (
        sea_events_df
        .groupBy("country_name", "ActionGeo_CountryCode")
        .agg(
            count("*").alias("spark_event_signal_count"),
            spark_sum("num_mentions").alias("spark_total_mentions"),
            spark_sum("num_sources").alias("spark_total_sources"),
            spark_sum("num_articles").alias("spark_total_articles"),
            avg("avg_tone").alias("spark_avg_tone"),
        )
        .orderBy(col("spark_event_signal_count").desc(), col("country_name"))
    )

    print("\nSpark SEA country summary:")
    summary_df.show(truncate=False)

    pandas_summary = summary_df.toPandas()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pandas_summary.to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved Spark demo output to: {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()