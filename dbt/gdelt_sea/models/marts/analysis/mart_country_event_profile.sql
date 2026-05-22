{{ config(materialized='table') }}

WITH country_event_counts AS (

    SELECT
        f.country_key,
        c.country_name,
        c.action_geo_country_code,

        f.event_code_key,
        e.event_base_code,
        e.event_root_code,
        e.quad_class,
        e.quad_class_label,
        e.is_conflict_quad,
        e.is_public_safety_signal,

        COUNT(*) AS event_signal_count,
        SUM(COALESCE(f.num_mentions, 0)) AS total_mentions,
        SUM(COALESCE(f.num_sources, 0)) AS total_sources,
        SUM(COALESCE(f.num_articles, 0)) AS total_articles,
        AVG(f.avg_tone) AS avg_tone,
        AVG(f.goldstein_scale) AS avg_goldstein_scale

    FROM {{ ref('fact_event_signal') }} f
    LEFT JOIN {{ ref('dim_country') }} c
        ON f.country_key = c.country_key
    LEFT JOIN {{ ref('dim_event_code') }} e
        ON f.event_code_key = e.event_code_key

    GROUP BY
        f.country_key,
        c.country_name,
        c.action_geo_country_code,
        f.event_code_key,
        e.event_base_code,
        e.event_root_code,
        e.quad_class,
        e.quad_class_label,
        e.is_conflict_quad,
        e.is_public_safety_signal

),

final AS (

    SELECT
        *,
        ROUND(
            event_signal_count * 1.0
            / SUM(event_signal_count) OVER (PARTITION BY country_key),
            4
        ) AS share_of_country_events,

        ROW_NUMBER() OVER (
            PARTITION BY country_key
            ORDER BY event_signal_count DESC, event_code_key
        ) AS country_event_rank

    FROM country_event_counts

)

SELECT *
FROM final
ORDER BY
    country_name,
    country_event_rank
