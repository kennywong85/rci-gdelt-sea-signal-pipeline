WITH row_counts AS (

    SELECT 'raw' AS layer_name, COUNT(*) AS row_count
    FROM {{ source('raw', 'gdelt_events') }}

    UNION ALL

    SELECT 'staging' AS layer_name, COUNT(*) AS row_count
    FROM {{ ref('stg_gdelt_events') }}

    UNION ALL

    SELECT 'fact' AS layer_name, COUNT(*) AS row_count
    FROM {{ ref('fact_event_signal') }}

),

summary AS (

    SELECT
        MIN(row_count) AS min_row_count,
        MAX(row_count) AS max_row_count
    FROM row_counts

)

SELECT *
FROM summary
WHERE min_row_count != max_row_count
