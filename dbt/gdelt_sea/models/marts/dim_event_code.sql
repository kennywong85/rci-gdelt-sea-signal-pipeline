{{ config(materialized='table') }}

SELECT
    event_code AS event_code_key,
    ANY_VALUE(event_base_code) AS event_base_code,
    ANY_VALUE(event_root_code) AS event_root_code,
    ANY_VALUE(quad_class) AS quad_class,
    ANY_VALUE(quad_class_label) AS quad_class_label,
    ANY_VALUE(is_conflict_quad) AS is_conflict_quad,
    ANY_VALUE(is_public_safety_signal) AS is_public_safety_signal,
    COUNT(*) AS sample_event_count

FROM {{ ref('stg_gdelt_events') }}
WHERE event_code IS NOT NULL
GROUP BY event_code
ORDER BY event_code
