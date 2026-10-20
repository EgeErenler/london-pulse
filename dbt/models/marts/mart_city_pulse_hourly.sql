-- One row per hour (London time): transport, bikes, weather and air side by side.
-- This is the table the dashboard uses to look for links, such as rain vs. bike use.
with lines as (
    select
        date_trunc('hour', captured_at_local)             as hour_local,
        count(distinct line_id) filter (where is_disrupted)
            / count(distinct captured_at_utc)             as avg_lines_disrupted
    from {{ ref('int_line_status__per_snapshot') }}
    group by 1
),

bikes as (
    select
        date_trunc('hour', captured_at_local)             as hour_local,
        avg(bikes_available)                              as avg_bikes_available,
        avg(network_occupancy)                            as avg_network_occupancy,
        avg(empty_stations)                               as avg_empty_stations
    from {{ ref('fct_bike_network_snapshots') }}
    group by 1
),

weather as (
    select
        date_trunc('hour', captured_at_local)             as hour_local,
        avg(temperature_c)                                as temperature_c,
        sum(precipitation_mm)                             as precipitation_mm,
        avg(wind_speed_kmh)                               as wind_speed_kmh
    from {{ ref('stg_open_meteo__weather') }}
    group by 1
),

air as (
    select
        date_trunc('hour', captured_at_local)             as hour_local,
        avg(european_aqi)                                 as european_aqi,
        avg(nitrogen_dioxide)                             as nitrogen_dioxide
    from {{ ref('stg_open_meteo__air_quality') }}
    group by 1
),

hours as (
    select hour_local from lines
    union select hour_local from bikes
    union select hour_local from weather
    union select hour_local from air
)

select
    hours.hour_local,
    round(lines.avg_lines_disrupted, 2)                   as avg_lines_disrupted,
    round(bikes.avg_bikes_available)                      as avg_bikes_available,
    round(bikes.avg_network_occupancy, 4)                 as avg_network_occupancy,
    round(bikes.avg_empty_stations, 1)                    as avg_empty_stations,
    round(weather.temperature_c, 1)                       as temperature_c,
    round(weather.precipitation_mm, 1)                    as precipitation_mm,
    round(weather.wind_speed_kmh, 1)                      as wind_speed_kmh,
    round(air.european_aqi, 1)                            as european_aqi,
    round(air.nitrogen_dioxide, 1)                        as nitrogen_dioxide
from hours
left join lines using (hour_local)
left join bikes using (hour_local)
left join weather using (hour_local)
left join air using (hour_local)
