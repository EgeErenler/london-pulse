-- When in the day do disruptions happen? Share of snapshots disrupted, by line and hour.
-- Hours when a line was closed (for example at night) are left out.
select
    line_id,
    any_value(line_name)                                  as line_name,
    hour(captured_at_local)                               as hour_of_day,
    count(*)                                              as snapshots,
    round(count(*) filter (where is_disrupted) / count(*), 4) as disrupted_share
from {{ ref('int_line_status__per_snapshot') }}
where not is_closed
group by 1, 3
