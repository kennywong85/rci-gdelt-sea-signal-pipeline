{{ config(materialized='table') }}

SELECT
    sea_country_key AS country_key,
    sea_country_name AS country_name,
    action_geo_country_code,
    region_name,
    notes

FROM {{ ref('stg_sea_countries') }}
