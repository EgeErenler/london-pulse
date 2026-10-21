-- "Service Closed" means the line is not meant to run. It must never count as a disruption,
-- and a snapshot cannot be closed and disrupted at the same time.
select line_id, captured_at_utc, status_description
from {{ ref('int_line_status__per_snapshot') }}
where is_closed and is_disrupted
