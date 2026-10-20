-- The latest known name and mode for every line.
select
    line_id,
    line_name,
    mode
from {{ ref('int_line_status__per_snapshot') }}
qualify row_number() over (partition by line_id order by captured_at_utc desc) = 1
