-- Shares and rates must always sit between 0 and 1. Any row returned is a failure.
select 'fct_line_status_daily' as model, good_service_share as value
from {{ ref('fct_line_status_daily') }}
where good_service_share not between 0 and 1

union all

select 'fct_disruptions_by_hour', disrupted_share
from {{ ref('fct_disruptions_by_hour') }}
where disrupted_share not between 0 and 1

union all

select 'fct_bike_network_snapshots', network_occupancy
from {{ ref('fct_bike_network_snapshots') }}
where network_occupancy not between 0 and 1
