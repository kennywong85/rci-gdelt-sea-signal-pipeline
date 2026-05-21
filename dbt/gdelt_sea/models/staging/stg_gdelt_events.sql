{{ config(materialized='view') }}

WITH source AS (

    SELECT *
    FROM {{ source('raw', 'gdelt_events') }}

),

typed AS (

    SELECT
        TRY_CAST(GLOBALEVENTID AS BIGINT) AS global_event_id,

        CAST(TRY_STRPTIME(SQLDATE, '%Y%m%d') AS DATE) AS event_date,
        TRY_CAST(MonthYear AS INTEGER) AS event_month_year,
        TRY_CAST(Year AS INTEGER) AS event_year,
        TRY_CAST(FractionDate AS DOUBLE) AS fraction_date,

        NULLIF(TRIM(Actor1Code), '') AS actor1_code,
        NULLIF(TRIM(Actor1Name), '') AS actor1_name,
        NULLIF(TRIM(Actor1CountryCode), '') AS actor1_country_code,
        NULLIF(TRIM(Actor1Type1Code), '') AS actor1_type1_code,
        NULLIF(TRIM(Actor1Type2Code), '') AS actor1_type2_code,
        NULLIF(TRIM(Actor1Type3Code), '') AS actor1_type3_code,

        NULLIF(TRIM(Actor2Code), '') AS actor2_code,
        NULLIF(TRIM(Actor2Name), '') AS actor2_name,
        NULLIF(TRIM(Actor2CountryCode), '') AS actor2_country_code,
        NULLIF(TRIM(Actor2Type1Code), '') AS actor2_type1_code,
        NULLIF(TRIM(Actor2Type2Code), '') AS actor2_type2_code,
        NULLIF(TRIM(Actor2Type3Code), '') AS actor2_type3_code,

        TRY_CAST(IsRootEvent AS INTEGER) AS is_root_event,

        NULLIF(TRIM(EventCode), '') AS event_code,
        NULLIF(TRIM(EventBaseCode), '') AS event_base_code,
        NULLIF(TRIM(EventRootCode), '') AS event_root_code,

        TRY_CAST(QuadClass AS INTEGER) AS quad_class,
        TRY_CAST(GoldsteinScale AS DOUBLE) AS goldstein_scale,

        TRY_CAST(NumMentions AS INTEGER) AS num_mentions,
        TRY_CAST(NumSources AS INTEGER) AS num_sources,
        TRY_CAST(NumArticles AS INTEGER) AS num_articles,
        TRY_CAST(AvgTone AS DOUBLE) AS avg_tone,

        NULLIF(TRIM(ActionGeo_Type), '') AS action_geo_type,
        NULLIF(TRIM(ActionGeo_FullName), '') AS action_geo_full_name,
        NULLIF(TRIM(ActionGeo_CountryCode), '') AS action_geo_country_code,
        NULLIF(TRIM(ActionGeo_ADM1Code), '') AS action_geo_adm1_code,
        NULLIF(TRIM(ActionGeo_ADM2Code), '') AS action_geo_adm2_code,
        TRY_CAST(ActionGeo_Lat AS DOUBLE) AS action_geo_lat,
        TRY_CAST(ActionGeo_Long AS DOUBLE) AS action_geo_long,
        NULLIF(TRIM(ActionGeo_FeatureID), '') AS action_geo_feature_id,

        NULLIF(TRIM(sea_country_name), '') AS sea_country_name,

        CAST(TRY_STRPTIME(DATEADDED, '%Y%m%d%H%M%S') AS TIMESTAMP) AS date_added,

        NULLIF(TRIM(SOURCEURL), '') AS source_url,

        filename AS source_file,
        loaded_at_utc

    FROM source

),

final AS (

    SELECT
        global_event_id,
        event_date,
        CAST(DATE_TRUNC('week', event_date) AS DATE) AS event_week_start,
        CAST(DATE_TRUNC('month', event_date) AS DATE) AS event_month_start,
        event_month_year,
        event_year,
        fraction_date,

        actor1_code,
        actor1_name,
        actor1_country_code,
        actor1_type1_code,
        actor1_type2_code,
        actor1_type3_code,

        actor2_code,
        actor2_name,
        actor2_country_code,
        actor2_type1_code,
        actor2_type2_code,
        actor2_type3_code,

        is_root_event,
        event_code,
        event_base_code,
        event_root_code,

        quad_class,

        CASE
            WHEN quad_class = 1 THEN 'Verbal Cooperation'
            WHEN quad_class = 2 THEN 'Material Cooperation'
            WHEN quad_class = 3 THEN 'Verbal Conflict'
            WHEN quad_class = 4 THEN 'Material Conflict'
            ELSE 'Unknown'
        END AS quad_class_label,

        CASE
            WHEN quad_class IN (3, 4) THEN TRUE
            ELSE FALSE
        END AS is_conflict_quad,

        CASE
            WHEN event_root_code IN ('14', '17', '18', '19', '20') THEN TRUE
            ELSE FALSE
        END AS is_public_safety_signal,

        goldstein_scale,
        num_mentions,
        num_sources,
        num_articles,
        avg_tone,

        action_geo_type,
        action_geo_full_name,
        action_geo_country_code,
        action_geo_adm1_code,
        action_geo_adm2_code,
        action_geo_lat,
        action_geo_long,
        action_geo_feature_id,

        sea_country_name,
        date_added,
        source_url,
        source_file,
        loaded_at_utc

    FROM typed

)

SELECT *
FROM final
