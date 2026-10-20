"""Write raw snapshots as Parquet, partitioned by day, and compact them later."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def to_frame(rows: list[dict], columns: dict[str, str]) -> pd.DataFrame:
    """Build a DataFrame with a fixed schema, so every file has the same column types."""
    frame = pd.DataFrame(rows, columns=list(columns))
    for name, dtype in columns.items():
        if dtype.startswith("datetime64"):
            frame[name] = pd.to_datetime(frame[name], utc=True).astype(dtype)
        else:
            frame[name] = frame[name].astype(dtype)
    return frame


def snapshot_path(raw_dir: Path, source: str, captured_at: datetime) -> Path:
    day = captured_at.strftime("%Y-%m-%d")
    stamp = captured_at.strftime("%H%M%S")
    return raw_dir / source / f"date={day}" / f"{source}_{stamp}.parquet"


def write_snapshot(
    rows: list[dict], columns: dict[str, str], raw_dir: Path, source: str, captured_at: datetime
) -> Path | None:
    if not rows:
        return None
    path = snapshot_path(raw_dir, source, captured_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    to_frame(rows, columns).to_parquet(path, index=False, compression="zstd")
    return path


def compact_partition(partition_dir: Path, source: str) -> Path | None:
    """Merge one day's many small snapshot files into a single file.

    Small files are fine for a few hours, but thousands of them slow every query down.
    """
    existing = sorted(partition_dir.glob("*_day.parquet"))
    files = sorted(p for p in partition_dir.glob("*.parquet") if p not in existing)
    if not files:
        return None
    frames = [pd.read_parquet(p) for p in existing + files]
    merged = pd.concat(frames, ignore_index=True).drop_duplicates()
    target = partition_dir / f"{source}_day.parquet"
    tmp = target.with_suffix(".tmp")
    merged.to_parquet(tmp, index=False, compression="zstd")
    for p in files:
        p.unlink()
    tmp.replace(target)
    return target
