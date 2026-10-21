"""Synthetic but realistic sample data.

Used by CI to test the dbt models end to end without calling real APIs,
and by anyone who wants to try the project offline.
"""

from __future__ import annotations

import math
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from london_pulse.sources import SOURCES
from london_pulse.storage import write_snapshot

LINES = [
    ("bakerloo", "Bakerloo", "tube"),
    ("central", "Central", "tube"),
    ("district", "District", "tube"),
    ("jubilee", "Jubilee", "tube"),
    ("northern", "Northern", "tube"),
    ("piccadilly", "Piccadilly", "tube"),
    ("victoria", "Victoria", "tube"),
    ("dlr", "DLR", "dlr"),
    ("elizabeth", "Elizabeth line", "elizabeth-line"),
    ("mildmay", "Mildmay", "overground"),
]
STATUSES = [(10, "Good Service"), (9, "Minor Delays"), (6, "Severe Delays"), (5, "Part Closure")]


def _rows_for(captured_at: datetime, rng: random.Random) -> dict[str, list[dict]]:
    hour = captured_at.hour
    rush = 1.0 if hour in (7, 8, 9, 17, 18, 19) else 0.0

    line_rows = []
    for line_id, name, mode in LINES:
        roll = rng.random()
        severity, desc = STATUSES[0]
        if roll < 0.04 + 0.08 * rush:
            severity, desc = STATUSES[1]
        elif roll < 0.05 + 0.1 * rush:
            severity, desc = STATUSES[2]
        line_rows.append(
            {
                "captured_at": captured_at,
                "line_id": line_id,
                "line_name": name,
                "mode": mode,
                "status_severity": severity,
                "status_description": desc,
                "reason": None if severity == 10 else f"{name}: {desc.lower()} (sample data)",
            }
        )

    bike_rows = []
    for i in range(1, 41):
        docks = 15 + (i * 7) % 20
        wave = math.sin(hour / 24 * 2 * math.pi + i)
        bikes = max(0, min(docks, int(docks * (0.5 + 0.35 * wave))))
        bike_rows.append(
            {
                "captured_at": captured_at,
                "station_id": f"BikePoints_{i}",
                "station_name": f"Sample Station {i}",
                "lat": 51.50 + (i % 8) * 0.008,
                "lon": -0.16 + (i // 8) * 0.015,
                "nb_bikes": bikes,
                "nb_standard_bikes": max(0, bikes - 2),
                "nb_ebikes": min(2, bikes),
                "nb_empty_docks": docks - bikes,
                "nb_docks": docks,
                "installed": True,
                "locked": False,
            }
        )

    temp = 12 + 5 * math.sin((hour - 9) / 24 * 2 * math.pi) + rng.uniform(-1, 1)
    rain = max(0.0, rng.gauss(0, 0.6))
    weather_rows = [
        {
            "captured_at": captured_at,
            "observed_at": captured_at,
            "temperature_c": round(temp, 1),
            "apparent_temperature_c": round(temp - 2, 1),
            "precipitation_mm": round(rain, 1),
            "rain_mm": round(rain, 1),
            "cloud_cover_pct": rng.randint(20, 100),
            "wind_speed_kmh": round(rng.uniform(5, 25), 1),
            "weather_code": 61 if rain > 0.5 else 3,
        }
    ]
    air_rows = [
        {
            "captured_at": captured_at,
            "observed_at": captured_at,
            "european_aqi": round(25 + 15 * rush + rng.uniform(-5, 5), 1),
            "pm2_5": round(rng.uniform(4, 14), 1),
            "pm10": round(rng.uniform(8, 22), 1),
            "nitrogen_dioxide": round(18 + 20 * rush + rng.uniform(-4, 4), 1),
            "ozone": round(rng.uniform(30, 60), 1),
        }
    ]
    return {
        "tfl_line_status": line_rows,
        "tfl_bikepoints": bike_rows,
        "weather": weather_rows,
        "air_quality": air_rows,
    }


def write_sample(raw_dir: Path, days: int = 3, seed: int = 7) -> None:
    rng = random.Random(seed)
    end = datetime.now(UTC).replace(minute=7, second=0, microsecond=0)
    start = end - timedelta(days=days)
    t = start
    while t <= end:
        for name, rows in _rows_for(t, rng).items():
            write_snapshot(rows, SOURCES[name].COLUMNS, raw_dir, name, t)
        t += timedelta(minutes=15)
