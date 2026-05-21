{{ config(materialized='table') }}

WITH actor_rows AS (

    SELECT
        actor1_code AS actor_code,
        actor1_name AS actor_name,
        actor1_country_code AS actor_country_code,
        actor1_type1_code AS actor_type1_code,
        actor1_type2_code AS actor_type2_code,
        actor1_type3_code AS actor_type3_code
    FROM {{ ref('stg_gdelt_events') }}

    UNION ALL

    SELECT
        actor2_code AS actor_code,
        actor2_name AS actor_name,
        actor2_country_code AS actor_country_code,
        actor2_type1_code AS actor_type1_code,
        actor2_type2_code AS actor_type2_code,
        actor2_type3_code AS actor_type3_code
    FROM {{ ref('stg_gdelt_events') }}

),

cleaned AS (

    SELECT DISTINCT
        MD5(
            COALESCE(actor_code, '') || '|' ||
            COALESCE(actor_name, '') || '|' ||
            COALESCE(actor_country_code, '') || '|' ||
            COALESCE(actor_type1_code, '') || '|' ||
            COALESCE(actor_type2_code, '') || '|' ||
            COALESCE(actor_type3_code, '')
        ) AS actor_key,
        actor_code,
        actor_name,
        actor_country_code,
        actor_type1_code,
        actor_type2_code,
        actor_type3_code

    FROM actor_rows
    WHERE
        actor_code IS NOT NULL
        OR actor_name IS NOT NULL
        OR actor_country_code IS NOT NULL
        OR actor_type1_code IS NOT NULL

)

SELECT *
FROM cleaned
ORDER BY actor_name, actor_code
