{{ config(severity = "warn") }}
-- Every snapshot must report each line once, and every line in every snapshot.
with per_snapshot as (
    select captured_at_utc, count(distinct line_id) as lines
    from {{ ref('int_line_status__per_snapshot') }}
    group by 1
)
select *
from per_snapshot
where lines <> (select count(*) from {{ ref('dim_lines') }})
