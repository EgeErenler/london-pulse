-- The whole Santander Cycles network at each snapshot.
select
    captured_at_utc,
    any_value(captured_at_local)                          as captured_at_local,
    count(*) filter (where is_in_service)                 as stations_in_service,
    sum(nb_bikes) filter (where is_in_service)            as bikes_available,
    sum(nb_ebikes) filter (where is_in_service)           as ebikes_available,
    sum(nb_docks) filter (where is_in_service)            as docks_total,
    count(*) filter (where is_in_service and is_empty)    as empty_stations,
    count(*) filter (where is_in_service and is_full)     as full_stations,
    round(
        sum(nb_bikes) filter (where is_in_service)
        / nullif(sum(nb_docks) filter (where is_in_service), 0),
        4
    )                                                     as network_occupancy
from {{ ref('stg_tfl__bikepoints') }}
group by 1
