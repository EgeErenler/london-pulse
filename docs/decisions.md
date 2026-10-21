# Design decisions

Short notes on why the project is built the way it is. Each one lists the trade-off, because
every choice here had a reasonable alternative.

## 1. Snapshots, not streams

TfL and Open-Meteo give the *current* state, not history. To study patterns, the pipeline
takes a snapshot every 15 minutes and keeps all of them.

- **Why 15 minutes:** frequent enough to catch most short disruptions and to see the morning
  and evening peaks clearly. Public repositories get free GitHub Actions minutes, and four
  calls an hour is still polite to public APIs. The first version used 30 minutes.
- **Trade-off:** more runs and more files. Daily compaction keeps the data branch small.
  Disruptions shorter than 15 minutes can still be missed.

## 2. GitHub Actions as the scheduler

A cron workflow runs `london-pulse ingest`. There is no server to pay for or patch.

- **Trade-off:** GitHub may start scheduled runs a few minutes late, and the timestamps in the
  data reflect when a run actually happened. For half-hourly snapshots that is acceptable.
  Airflow or Dagster would give retries and backfills, but would be heavy for four sources.

## 3. Raw data as Parquet on a separate `data` branch

Each snapshot is written as a small Parquet file, partitioned by day
(`raw/<source>/date=YYYY-MM-DD/`). The files live on an orphan `data` branch, so `main`
contains only code.

- **Why Parquet:** columnar, compressed and typed. DuckDB reads it directly, so there is no
  load step.
- **Why a branch, not S3 or a database:** free, versioned and visible to anyone who wants
  the data. A daily job merges each day into one file and squashes the branch history, so the
  repository does not grow without limit.
- **Trade-off:** git is not a data lake. At much larger volumes this should move to object
  storage (S3, R2 or GCS) with the same folder layout.

## 4. One failing API must not stop the others

`ingest` catches errors per source, logs them and carries on. The run only fails when *every*
source fails. Partial data is still useful, and a red run on every short TfL outage would hide
real problems.

## 5. A fixed schema in code

Every source declares its columns and types (`COLUMNS`), and each file is written with exactly
that schema. TfL returns counts as strings and sometimes as empty strings, so parsing is
defensive and tested with real-shaped fixtures.

## 6. dbt on DuckDB for modelling

- **Staging** models clean and type the raw data, one model per source.
- **Intermediate** models apply business rules, for example keeping only the most serious
  status when a line reports several at once.
- **Marts** are the tables the dashboard reads.

DuckDB runs in-process, so the full model build takes seconds in CI. The same SQL would move
to Snowflake or BigQuery with small changes.

## 7. What counts as "disrupted"

TfL publishes a severity code for each status. Codes 10 (Good Service), 18 (No Issues),
19 (Information) and 20 (Service Closed, for example at night) count as normal. Everything
else, from Minor Delays to Suspended, counts as disrupted. This rule lives in one macro
(`tfl_normal_severities`), so it can change in one place.

## 8. Tests at two levels

- **pytest** checks the Python: parsing, schemas, compaction and failure handling.
- **dbt tests** check the data: keys are unique, shares stay between 0 and 1, every line in
  a fact table exists in `dim_lines`. A warning test watches for stations that report more
  bikes than docks.

CI runs both against synthetic sample data, so pull requests are tested without calling
real APIs.

## 9. A static dashboard

The dashboard is a single HTML page built from the marts and published to GitHub Pages.

- **Why static:** it loads fast, costs nothing and cannot go down because a server is asleep.
- **Trade-off:** it is only as fresh as the last build (every two hours). A Streamlit or
  Evidence app would allow live filtering, at the cost of a running service.

## Ideas for later

- Move raw storage to object storage once it passes a few hundred MB.
- Add bus and river services from the same TfL API.
- Alert on unusual disruption levels (for example with a z-score per line and hour).
