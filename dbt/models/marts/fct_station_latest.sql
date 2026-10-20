-- The most recent reading for every docking station, for the map.
select
    station_id,
    station_name,
    lat,
    lon,
    nb_bikes,
    nb_ebikes,
    nb_empty_docks,
    nb_docks,
    occupancy_rate,
    is_in_service,
    captured_at_utc
from {{ ref('stg_tfl__bikepoints') }}
qualify row_number() over (partition by station_id order by captured_at_utc desc) = 1
