{#- Read every Parquet snapshot of one source, across all day partitions. -#}
{% macro raw_snapshots(source_name) -%}
read_parquet(
    '{{ var("raw_path") }}/{{ source_name }}/*/*.parquet',
    hive_partitioning = true,
    union_by_name = true
)
{%- endmacro %}

{#- TfL severities that mean the line is running normally or is closed on purpose. -#}
{% macro tfl_normal_severities() -%}
(10, 18, 19, 20)
{%- endmacro %}
