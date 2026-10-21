-- Reliability counts only snapshots when the line was meant to run.
select service_date, line_id
from {{ ref('fct_line_status_daily') }}
where disrupted_snapshots > in_service_snapshots
   or (in_service_snapshots = 0 and good_service_share is not null)
