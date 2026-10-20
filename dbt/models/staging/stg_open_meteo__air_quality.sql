with source as (
    select * from {{ raw_snapshots('air_quality') }}
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
    european_aqi,
    pm2_5,
    pm10,
    nitrogen_dioxide,
    ozone,
    -- European AQI bands, as published by the European Environment Agency.
    case
        when european_aqi is null then null
        when european_aqi <= 20 then 'Good'
        when european_aqi <= 40 then 'Fair'
        when european_aqi <= 60 then 'Moderate'
        when european_aqi <= 80 then 'Poor'
        when european_aqi <= 100 then 'Very poor'
        else 'Extremely poor'
    end                                       as aqi_band
from deduplicated
