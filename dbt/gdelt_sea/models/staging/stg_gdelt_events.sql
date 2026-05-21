{{ config(materialized='view') }}

SELECT
    TRY_CAST(GLOBALEVENTID AS BIGINT) AS global_event_id,
    CAST(TRY_STRPTIME(SQLDATE, '%Y%m%d') AS DATE) AS event_date,
    TRY_CAST(MonthYear AS INTEGER) AS month_year,
    TRY_CAST(Year AS INTEGER) AS event_year,
    TRY_CAST(FractionDate AS DOUBLE) AS fraction_date,

    Actor1Code AS actor1_code,
    Actor1Name AS actor1_name,
    Actor1CountryCode AS actor1_country_code,
    Actor1Type1Code AS actor1_type1_code,
    Actor1Type2Code AS actor1_type2_code,
    Actor1Type3Code AS actor1_type3_code,

    Actor2Code AS actor2_code,
    Actor2Name AS actor2_name,
    Actor2CountryCode AS actor2_country_code,
    Actor2Type1Code AS actor2_type1_code,
    Actor2Type2Code AS actor2_type2_code,
    Actor2Type3Code AS actor2_type3_code,

    TRY_CAST(IsRootEvent AS INTEGER) AS is_root_event,
    EventCode AS event_code,
    EventBaseCode AS event_base_code,
    EventRootCode AS event_root_code,
    TRY_CAST(QuadClass AS INTEGER) AS quad_class,
    TRY_CAST(GoldsteinScale AS DOUBLE) AS goldstein_scale,

    TRY_CAST(NumMentions AS INTEGER) AS num_mentions,
    TRY_CAST(NumSources AS INTEGER) AS num_sources,
    TRY_CAST(NumArticles AS INTEGER) AS num_articles,
    TRY_CAST(AvgTone AS DOUBLE) AS avg_tone,

    ActionGeo_Type AS action_geo_type,
    ActionGeo_FullName AS action_geo_full_name,
    ActionGeo_CountryCode AS action_geo_country_code,
    ActionGeo_ADM1Code AS action_geo_adm1_code,
    ActionGeo_ADM2Code AS action_geo_adm2_code,
    TRY_CAST(ActionGeo_Lat AS DOUBLE) AS action_geo_lat,
    TRY_CAST(ActionGeo_Long AS DOUBLE) AS action_geo_long,
    ActionGeo_FeatureID AS action_geo_feature_id,

    sea_country_name,

    CAST(TRY_STRPTIME(DATEADDED, '%Y%m%d%H%M%S') AS TIMESTAMP) AS date_added,
    SOURCEURL AS source_url,

    filename AS source_file,
    loaded_at_utc

FROM {{ source('raw', 'gdelt_events') }}
