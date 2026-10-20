from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
import responses

from london_pulse.cli import run_compact, run_ingest
from london_pulse.config import OPEN_METEO_AIR_URL, OPEN_METEO_WEATHER_URL, TFL_BASE_URL, Settings
from london_pulse.sources import bikepoints, line_status
from london_pulse.storage import compact_partition, snapshot_path, write_snapshot


def test_snapshot_path_is_partitioned_by_day(tmp_path, captured_at):
    path = snapshot_path(tmp_path, "weather", captured_at)
    assert path == tmp_path / "weather" / "date=2026-10-21" / "weather_080700.parquet"


def test_write_snapshot_keeps_schema(tmp_path, load_fixture, captured_at):
    rows = bikepoints.parse(load_fixture("bikepoints.json"), captured_at)
    path = write_snapshot(rows, bikepoints.COLUMNS, tmp_path, "tfl_bikepoints", captured_at)

    frame = pd.read_parquet(path)
    assert list(frame.columns) == list(bikepoints.COLUMNS)
    assert str(frame["nb_bikes"].dtype) == "Int64"
    assert frame["nb_bikes"].isna().sum() == 1


def test_write_snapshot_skips_empty(tmp_path, captured_at):
    assert write_snapshot([], line_status.COLUMNS, tmp_path, "tfl_line_status", captured_at) is None


def test_compact_merges_files(tmp_path, load_fixture):
    base = datetime(2026, 10, 20, 8, 0, tzinfo=UTC)
    for minutes in (0, 30, 60):
        t = base + timedelta(minutes=minutes)
        rows = line_status.parse(load_fixture("line_status.json"), t)
        write_snapshot(rows, line_status.COLUMNS, tmp_path, "tfl_line_status", t)

    partition = tmp_path / "tfl_line_status" / "date=2026-10-20"
    target = compact_partition(partition, "tfl_line_status")

    assert [p.name for p in partition.iterdir()] == ["tfl_line_status_day.parquet"]
    assert len(pd.read_parquet(target)) == 12


def test_run_compact_leaves_today_alone(tmp_path, load_fixture):
    settings = Settings(data_dir=tmp_path)
    now = datetime.now(UTC)
    for t in (now, now + timedelta(seconds=1)):
        rows = line_status.parse(load_fixture("line_status.json"), t)
        write_snapshot(rows, line_status.COLUMNS, settings.raw_dir, "tfl_line_status", t)

    run_compact(settings)

    today = settings.raw_dir / "tfl_line_status" / f"date={now:%Y-%m-%d}"
    assert len(list(today.glob("*.parquet"))) == 2


@responses.activate
def test_ingest_survives_one_failing_source(tmp_path, load_fixture):
    responses.get(
        f"{TFL_BASE_URL}/Line/Mode/tube,overground,dlr,elizabeth-line/Status",
        json=load_fixture("line_status.json"),
    )
    responses.get(f"{TFL_BASE_URL}/BikePoint", json=load_fixture("bikepoints.json"))
    responses.get(OPEN_METEO_WEATHER_URL, json={"current": {"time": "2026-10-21T08:00"}})
    responses.get(OPEN_METEO_AIR_URL, status=404)  # not retried, fails fast

    code = run_ingest(Settings(data_dir=tmp_path, timeout_seconds=2))

    assert code == 0
    written = sorted(p.parent.parent.name for p in tmp_path.rglob("*.parquet"))
    assert written == ["tfl_bikepoints", "tfl_line_status", "weather"]
