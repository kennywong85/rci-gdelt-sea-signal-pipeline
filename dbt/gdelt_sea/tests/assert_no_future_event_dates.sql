SELECT
    global_event_id,
    event_date
FROM {{ ref('stg_gdelt_events') }}
WHERE event_date > CURRENT_DATE
