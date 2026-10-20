-- The intermediate model must keep exactly one status per line per snapshot.
select line_id, captured_at_utc, count(*) as rows_found
from {{ ref('int_line_status__per_snapshot') }}
group by 1, 2
having count(*) > 1
