WITH mart_counts AS (

    SELECT
        'mart_regional_spike_monitoring' AS mart_name,
        COUNT(*) AS row_count
    FROM {{ ref('mart_regional_spike_monitoring') }}

    UNION ALL

    SELECT
        'mart_country_event_profile' AS mart_name,
        COUNT(*) AS row_count
    FROM {{ ref('mart_country_event_profile') }}

    UNION ALL

    SELECT
        'mart_country_actor_profile' AS mart_name,
        COUNT(*) AS row_count
    FROM {{ ref('mart_country_actor_profile') }}

)

SELECT *
FROM mart_counts
WHERE row_count = 0
