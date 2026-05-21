{{ config(materialized='table') }}

WITH dates AS (

    SELECT DISTINCT
        event_date
    FROM {{ ref('stg_gdelt_events') }}
    WHERE event_date IS NOT NULL

)

SELECT
    CAST(STRFTIME(event_date, '%Y%m%d') AS INTEGER) AS date_key,
    event_date,
    CAST(DATE_TRUNC('week', event_date) AS DATE) AS week_start_date,
    CAST(DATE_TRUNC('month', event_date) AS DATE) AS month_start_date,
    EXTRACT(YEAR FROM event_date) AS year,
    EXTRACT(QUARTER FROM event_date) AS quarter,
    EXTRACT(MONTH FROM event_date) AS month,
    STRFTIME(event_date, '%Y-%m') AS year_month,
    STRFTIME(event_date, '%A') AS day_name

FROM dates
ORDER BY event_date
