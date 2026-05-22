SELECT
    global_event_id,
    event_date,
    event_week_start,
    event_month_start
FROM {{ ref('stg_gdelt_events') }}
WHERE
    event_week_start != CAST(DATE_TRUNC('week', event_date) AS DATE)
    OR event_month_start != CAST(DATE_TRUNC('month', event_date) AS DATE)
