-- One row per line status reported in a snapshot. A line can report several at once.
with source as (
    select * from {{ raw_snapshots('tfl_line_status') }}
)

select
    timezone('UTC', captured_at)              as captured_at_utc,
    timezone('Europe/London', captured_at)    as captured_at_local,
    line_id,
    line_name,
    mode,
    cast(status_severity as integer)          as status_severity,
    coalesce(status_description, 'Unknown')   as status_description,
    reason,
    coalesce(status_severity = {{ tfl_closed_severity() }}, false) as is_closed,
    status_severity is not null
        and status_severity not in {{ tfl_normal_severities() }}
        and status_severity <> {{ tfl_closed_severity() }} as is_disrupted
from source
where line_id is not null
