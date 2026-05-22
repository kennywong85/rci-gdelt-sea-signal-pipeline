SELECT
    e.global_event_id,
    e.sea_country_name,
    e.action_geo_country_code
FROM {{ ref('stg_gdelt_events') }} e
LEFT JOIN {{ ref('stg_sea_countries') }} c
    ON e.sea_country_name = c.sea_country_name
    AND e.action_geo_country_code = c.action_geo_country_code
WHERE c.sea_country_key IS NULL
