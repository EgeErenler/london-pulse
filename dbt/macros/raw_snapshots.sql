{#- Read every Parquet snapshot of one source, across all day partitions. -#}
{% macro raw_snapshots(source_name) -%}
read_parquet(
    '{{ var("raw_path") }}/{{ source_name }}/*/*.parquet',
    hive_partitioning = true,
    union_by_name = true
)
{%- endmacro %}

{#- TfL severities that mean the line is running normally: Good Service, No Issues, Information. -#}
{% macro tfl_normal_severities() -%}
(10, 18, 19)
{%- endmacro %}

{#- TfL severity 20 is "Service Closed": the line is not meant to run (for example at night).
    It is neither good service nor a disruption, so reliability leaves it out. -#}
{% macro tfl_closed_severity() -%}
20
{%- endmacro %}
