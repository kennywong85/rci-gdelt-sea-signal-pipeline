{{ config(materialized='table') }}

WITH events AS (

    SELECT *
    FROM {{ ref('stg_gdelt_events') }}

),

country_dim AS (

    SELECT *
    FROM {{ ref('dim_country') }}

),

final AS (

    SELECT
        e.global_event_id AS event_signal_key,
        e.global_event_id,

        CAST(STRFTIME(e.event_date, '%Y%m%d') AS INTEGER) AS date_key,
        c.country_key,
        e.event_code AS event_code_key,

        CASE
            WHEN
                e.actor1_code IS NOT NULL
                OR e.actor1_name IS NOT NULL
                OR e.actor1_country_code IS NOT NULL
                OR e.actor1_type1_code IS NOT NULL
            THEN MD5(
                COALESCE(e.actor1_code, '') || '|' ||
                COALESCE(e.actor1_name, '') || '|' ||
                COALESCE(e.actor1_country_code, '') || '|' ||
                COALESCE(e.actor1_type1_code, '') || '|' ||
                COALESCE(e.actor1_type2_code, '') || '|' ||
                COALESCE(e.actor1_type3_code, '')
            )
        END AS actor1_key,

        CASE
            WHEN
                e.actor2_code IS NOT NULL
                OR e.actor2_name IS NOT NULL
                OR e.actor2_country_code IS NOT NULL
                OR e.actor2_type1_code IS NOT NULL
            THEN MD5(
                COALESCE(e.actor2_code, '') || '|' ||
                COALESCE(e.actor2_name, '') || '|' ||
                COALESCE(e.actor2_country_code, '') || '|' ||
                COALESCE(e.actor2_type1_code, '') || '|' ||
                COALESCE(e.actor2_type2_code, '') || '|' ||
                COALESCE(e.actor2_type3_code, '')
            )
        END AS actor2_key,

        e.event_date,
        e.event_week_start,
        e.event_month_start,

        e.action_geo_full_name,
        e.action_geo_country_code,
        e.action_geo_adm1_code,
        e.action_geo_adm2_code,
        e.action_geo_lat,
        e.action_geo_long,

        1 AS event_count,
        e.num_mentions,
        e.num_sources,
        e.num_articles,
        e.avg_tone,
        e.goldstein_scale,

        e.quad_class,
        e.quad_class_label,
        e.is_conflict_quad,
        e.is_public_safety_signal,

        e.source_url,
        e.source_file,
        e.loaded_at_utc

    FROM events e
    LEFT JOIN country_dim c
        ON e.sea_country_name = c.country_name
        AND e.action_geo_country_code = c.action_geo_country_code

)

SELECT *
FROM final
