-- How reliable was each line on each day (London time)?
-- Only snapshots when the line was meant to run count; "Service Closed" is left out.
with snapshots as (
    select * from {{ ref('int_line_status__per_snapshot') }}
)

select
    cast(captured_at_local as date)                       as service_date,
    line_id,
    any_value(line_name)                                  as line_name,
    any_value(mode)                                       as mode,
    count(*)                                              as snapshots,
    count(*) filter (where not is_closed)                 as in_service_snapshots,
    count(*) filter (where is_disrupted)                  as disrupted_snapshots,
    round(
        1 - count(*) filter (where is_disrupted)
            / nullif(count(*) filter (where not is_closed), 0),
        4
    )                                                     as good_service_share,
    arg_min(status_description, status_severity)
        filter (where is_disrupted)                       as worst_status
from snapshots
group by 1, 2
