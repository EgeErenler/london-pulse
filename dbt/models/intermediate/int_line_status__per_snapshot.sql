-- Collapse to one row per line per snapshot, keeping the most serious status.
-- Lower TfL severity numbers are more serious, among the statuses that count as disrupted.
with statuses as (
    select * from {{ ref('stg_tfl__line_status') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by line_id, captured_at_utc
            order by is_disrupted desc, is_closed asc, status_severity asc
        ) as rank_in_snapshot,
        string_agg(distinct reason, ' | ') over (
            partition by line_id, captured_at_utc
        ) as all_reasons
    from statuses
)

select
    captured_at_utc,
    captured_at_local,
    line_id,
    line_name,
    mode,
    status_severity,
    status_description,
    is_closed,
    is_disrupted,
    all_reasons as reason
from ranked
where rank_in_snapshot = 1
