with source as (
    select * from {{ raw_snapshots('weather') }}
),

deduplicated as (
    select *
    from source
    qualify row_number() over (partition by captured_at order by observed_at desc) = 1
)

select
    timezone('UTC', captured_at)              as captured_at_utc,
    timezone('Europe/London', captured_at)    as captured_at_local,
    timezone('UTC', observed_at)              as observed_at_utc,
    temperature_c,
    apparent_temperature_c,
    precipitation_mm,
    rain_mm,
    cloud_cover_pct,
    wind_speed_kmh,
    weather_code,
    precipitation_mm > 0                      as is_wet
from deduplicated
