"""Command line entry point: `london-pulse ingest | compact | sample | dashboard`."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from london_pulse.config import Settings
from london_pulse.http import build_session
from london_pulse.sources import SOURCES
from london_pulse.storage import compact_partition, write_snapshot

log = logging.getLogger("london_pulse")


def run_ingest(settings: Settings, only: list[str] | None = None) -> int:
    """Fetch every source once. One failing API must not stop the others."""
    captured_at = datetime.now(UTC).replace(microsecond=0)
    session = build_session(settings)
    failures = 0
    names = only or list(SOURCES)
    for name in names:
        module = SOURCES[name]
        try:
            rows = module.fetch(session, settings, captured_at)
            path = write_snapshot(rows, module.COLUMNS, settings.raw_dir, name, captured_at)
            log.info("%-16s %5d rows -> %s", name, len(rows), path)
        except Exception as exc:  # noqa: BLE001 - we log and carry on by design
            failures += 1
            log.error("%-16s failed: %s", name, exc)
    # Partial data is still useful; only fail the run when nothing at all was collected.
    return 1 if failures == len(names) else 0


def run_compact(settings: Settings, keep_days: int = 1) -> int:
    """Merge snapshot files for every finished day (today is left alone)."""
    cutoff = (datetime.now(UTC) - timedelta(days=keep_days - 1)).strftime("%Y-%m-%d")
    merged = 0
    for name in SOURCES:
        for partition in sorted((settings.raw_dir / name).glob("date=*")):
            if partition.name.split("=", 1)[1] < cutoff and compact_partition(partition, name):
                merged += 1
    log.info("compacted %d partitions", merged)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="london-pulse", description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="fetch one snapshot from every source")
    ingest.add_argument("--source", action="append", choices=sorted(SOURCES))

    sub.add_parser("compact", help="merge small snapshot files of finished days")

    sample = sub.add_parser("sample", help="write synthetic sample data (for tests and demos)")
    sample.add_argument("--days", type=int, default=3)

    dash = sub.add_parser("dashboard", help="build the static dashboard from the dbt database")
    dash.add_argument("--db", type=Path, default=Path("london_pulse.duckdb"))
    dash.add_argument("--out", type=Path, default=Path("site"))

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    settings = Settings()

    if args.command == "ingest":
        return run_ingest(settings, args.source)
    if args.command == "compact":
        return run_compact(settings)
    if args.command == "sample":
        from london_pulse.sample import write_sample

        write_sample(settings.raw_dir, days=args.days)
        return 0
    if args.command == "dashboard":
        from london_pulse.dashboard import build_dashboard

        build_dashboard(args.db, args.out)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
