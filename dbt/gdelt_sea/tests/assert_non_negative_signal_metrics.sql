SELECT
    event_signal_key,
    event_count,
    num_mentions,
    num_sources,
    num_articles
FROM {{ ref('fact_event_signal') }}
WHERE
    event_count < 0
    OR num_mentions < 0
    OR num_sources < 0
    OR num_articles < 0
