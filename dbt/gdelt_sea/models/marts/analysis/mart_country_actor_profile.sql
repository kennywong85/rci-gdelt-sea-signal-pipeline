{{ config(materialized='table') }}

WITH actor_events AS (

    SELECT
        country_key,
        actor1_key AS actor_key,
        'Actor 1' AS actor_position,
        event_signal_key,
        is_conflict_quad,
        is_public_safety_signal,
        num_mentions,
        num_sources,
        num_articles,
        avg_tone,
        goldstein_scale
    FROM {{ ref('fact_event_signal') }}
    WHERE actor1_key IS NOT NULL

    UNION ALL

    SELECT
        country_key,
        actor2_key AS actor_key,
        'Actor 2' AS actor_position,
        event_signal_key,
        is_conflict_quad,
        is_public_safety_signal,
        num_mentions,
        num_sources,
        num_articles,
        avg_tone,
        goldstein_scale
    FROM {{ ref('fact_event_signal') }}
    WHERE actor2_key IS NOT NULL

),

actor_counts AS (

    SELECT
        ae.country_key,
        c.country_name,
        c.action_geo_country_code,

        ae.actor_key,
        a.actor_code,
        a.actor_name,
        a.actor_country_code,
        a.actor_type1_code,
        a.actor_type2_code,
        a.actor_type3_code,

        ae.actor_position,

        COUNT(*) AS actor_event_signal_count,
        SUM(CASE WHEN ae.is_conflict_quad THEN 1 ELSE 0 END) AS conflict_signal_count,
        SUM(CASE WHEN ae.is_public_safety_signal THEN 1 ELSE 0 END) AS public_safety_signal_count,

        SUM(COALESCE(ae.num_mentions, 0)) AS total_mentions,
        SUM(COALESCE(ae.num_sources, 0)) AS total_sources,
        SUM(COALESCE(ae.num_articles, 0)) AS total_articles,
        AVG(ae.avg_tone) AS avg_tone,
        AVG(ae.goldstein_scale) AS avg_goldstein_scale

    FROM actor_events ae
    LEFT JOIN {{ ref('dim_country') }} c
        ON ae.country_key = c.country_key
    LEFT JOIN {{ ref('dim_actor') }} a
        ON ae.actor_key = a.actor_key

    GROUP BY
        ae.country_key,
        c.country_name,
        c.action_geo_country_code,
        ae.actor_key,
        a.actor_code,
        a.actor_name,
        a.actor_country_code,
        a.actor_type1_code,
        a.actor_type2_code,
        a.actor_type3_code,
        ae.actor_position

),

final AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY country_key
            ORDER BY actor_event_signal_count DESC, actor_name, actor_code
        ) AS country_actor_rank

    FROM actor_counts

)

SELECT *
FROM final
ORDER BY
    country_name,
    country_actor_rank
