{{ config(materialized='table') }}

WITH weekly_country_signals AS (

    SELECT
        f.country_key,
        c.country_name,
        c.action_geo_country_code,
        f.event_week_start AS week_start_date,

        COUNT(*) AS event_signal_count,

        SUM(CASE WHEN f.is_conflict_quad THEN 1 ELSE 0 END) AS conflict_signal_count,
        SUM(CASE WHEN f.is_public_safety_signal THEN 1 ELSE 0 END) AS public_safety_signal_count,

        SUM(COALESCE(f.num_mentions, 0)) AS total_mentions,
        SUM(COALESCE(f.num_sources, 0)) AS total_sources,
        SUM(COALESCE(f.num_articles, 0)) AS total_articles,

        AVG(f.avg_tone) AS avg_tone,
        AVG(f.goldstein_scale) AS avg_goldstein_scale

    FROM {{ ref('fact_event_signal') }} f
    LEFT JOIN {{ ref('dim_country') }} c
        ON f.country_key = c.country_key

    GROUP BY
        f.country_key,
        c.country_name,
        c.action_geo_country_code,
        f.event_week_start

),

with_trends AS (

    SELECT
        *,
        LAG(event_signal_count) OVER (
            PARTITION BY country_key
            ORDER BY week_start_date
        ) AS previous_week_event_signal_count,

        event_signal_count
            - COALESCE(
                LAG(event_signal_count) OVER (
                    PARTITION BY country_key
                    ORDER BY week_start_date
                ),
                0
            ) AS week_on_week_change,

        CASE
            WHEN LAG(event_signal_count) OVER (
                PARTITION BY country_key
                ORDER BY week_start_date
            ) IS NULL THEN NULL

            WHEN LAG(event_signal_count) OVER (
                PARTITION BY country_key
                ORDER BY week_start_date
            ) = 0 THEN NULL

            ELSE ROUND(
                event_signal_count * 1.0
                / LAG(event_signal_count) OVER (
                    PARTITION BY country_key
                    ORDER BY week_start_date
                ),
                2
            )
        END AS week_on_week_ratio

    FROM weekly_country_signals

)

SELECT
    country_key,
    country_name,
    action_geo_country_code,
    week_start_date,

    event_signal_count,
    previous_week_event_signal_count,
    week_on_week_change,
    week_on_week_ratio,

    conflict_signal_count,
    public_safety_signal_count,

    total_mentions,
    total_sources,
    total_articles,

    avg_tone,
    avg_goldstein_scale,

    CASE
        WHEN previous_week_event_signal_count IS NULL THEN 'No prior week'
        WHEN week_on_week_ratio >= 2.0 AND event_signal_count >= 10 THEN 'Possible spike'
        WHEN week_on_week_change >= 10 THEN 'Possible spike'
        ELSE 'Normal / monitor'
    END AS spike_flag

FROM with_trends
ORDER BY
    week_start_date DESC,
    event_signal_count DESC,
    country_name
