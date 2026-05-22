SELECT
    event_signal_key,
    event_count
FROM {{ ref('fact_event_signal') }}
WHERE event_count != 1
