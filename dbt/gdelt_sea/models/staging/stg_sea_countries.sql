{{ config(materialized='view') }}

SELECT
    ROW_NUMBER() OVER (ORDER BY country_name) AS sea_country_key,
    country_name AS sea_country_name,
    gdelt_fips_code AS action_geo_country_code,
    'Southeast Asia' AS region_name,
    NULLIF(TRIM(notes), '') AS notes

FROM {{ source('metadata', 'sea_country_lookup') }}
