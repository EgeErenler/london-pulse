-- One row per docking station per snapshot.
with source as (
    select * from {{ raw_snapshots('tfl_bikepoints') }}
)

select
    timezone('UTC', captured_at)              as captured_at_utc,
    timezone('Europe/London', captured_at)    as captured_at_local,
    station_id,
    trim(station_name)                        as station_name,
    lat,
    lon,
    nb_bikes,
    nb_standard_bikes,
    nb_ebikes,
    nb_empty_docks,
    nb_docks,
    coalesce(installed, false) and not coalesce(locked, false) as is_in_service,
    nb_bikes = 0                              as is_empty,
    nb_empty_docks = 0                        as is_full,
    nb_bikes::double / nullif(nb_docks, 0)    as occupancy_rate
from source
where station_id is not null
