{{ config(severity = 'warn') }}
-- A station should never report more bikes than docks. TfL data is not perfect,
-- so this is a warning that we watch, not a hard failure.
select station_id, captured_at_utc, nb_bikes, nb_docks
from {{ ref('stg_tfl__bikepoints') }}
where nb_bikes > nb_docks
