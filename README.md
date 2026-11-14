# London Pulse: raw data

This branch holds the raw snapshots collected by the
[Ingest workflow](https://github.com/EgeErenler/london-pulse/actions/workflows/ingest.yml).

```
raw/<source>/date=YYYY-MM-DD/<source>_HHMMSS.parquet   snapshots of the current day
raw/<source>/date=YYYY-MM-DD/<source>_day.parquet      one merged file per finished day
```

The history of this branch is squashed once a day to keep the repository small.
Code and documentation live on [`main`](https://github.com/EgeErenler/london-pulse).
