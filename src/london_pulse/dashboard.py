"""Build a static HTML dashboard from the dbt marts. No server needed, so it can live on Pages."""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime
from decimal import Decimal
from importlib.resources import files
from pathlib import Path
from typing import Any

import duckdb
from jinja2 import Template

log = logging.getLogger(__name__)

# Official TfL line colours, so the charts look familiar to Londoners.
LINE_COLOURS = {
    "bakerloo": "#B36305",
    "central": "#E32017",
    "circle": "#FFD300",
    "district": "#00782A",
    "hammersmith-city": "#F3A9BB",
    "jubilee": "#A0A5A9",
    "metropolitan": "#9B0056",
    "northern": "#8C8C8C",
    "piccadilly": "#1C4FA0",
    "victoria": "#0098D4",
    "waterloo-city": "#95CDBA",
    "dlr": "#00A4A7",
    "elizabeth": "#6950A1",
    "liberty": "#61686B",
    "lioness": "#FAA61A",
    "mildmay": "#437EC1",
    "suffragette": "#18A95D",
    "weaver": "#9B4F9F",
    "windrush": "#EF4D5E",
}

# WMO weather codes used by Open-Meteo.
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Rain showers",
    82: "Violent showers",
    95: "Thunderstorm",
}

QUERIES = {
    "now_lines": """
        select line_id, line_name, mode, status_description, is_disrupted, reason
        from main_intermediate.int_line_status__per_snapshot
        where captured_at_utc = (
            select max(captured_at_utc) from main_intermediate.int_line_status__per_snapshot
        )
        order by is_disrupted desc, line_name
    """,
    "now_bikes": """
        select * from main.fct_bike_network_snapshots
        order by captured_at_utc desc limit 1
    """,
    "now_weather": """
        select * from main_staging.stg_open_meteo__weather
        order by captured_at_utc desc limit 1
    """,
    "now_air": """
        select * from main_staging.stg_open_meteo__air_quality
        order by captured_at_utc desc limit 1
    """,
    "reliability": """
        select line_id, any_value(line_name) as line_name,
               round(sum(snapshots - disrupted_snapshots) / sum(snapshots), 4) as good_share,
               sum(snapshots) as snapshots
        from main.fct_line_status_daily
        where service_date >= current_date - interval 7 day
        group by 1
        order by good_share desc, line_name desc
    """,
    "by_hour": """
        select line_id, line_name, hour_of_day, disrupted_share
        from main.fct_disruptions_by_hour
        order by line_name, hour_of_day
    """,
    "pulse": """
        select * from main.mart_city_pulse_hourly
        where hour_local >= (select max(hour_local) from main.mart_city_pulse_hourly)
                            - interval 72 hour
        order by hour_local
    """,
    "stations": """
        select station_name, lat, lon, nb_bikes, nb_ebikes, nb_empty_docks, nb_docks,
               occupancy_rate
        from main.fct_station_latest
        where is_in_service
    """,
    "coverage": """
        select min(captured_at_utc) as first_snapshot, max(captured_at_utc) as last_snapshot,
               count(*) as snapshots
        from main.fct_bike_network_snapshots
    """,
}


def _clean(value: Any) -> Any:
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _rows(con: duckdb.DuckDBPyConnection, sql: str) -> list[dict[str, Any]]:
    cursor = con.execute(sql)
    names = [d[0] for d in cursor.description]
    return [{n: _clean(v) for n, v in zip(names, row, strict=True)} for row in cursor.fetchall()]


def collect(db_path: Path) -> dict[str, Any]:
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        data = {name: _rows(con, sql) for name, sql in QUERIES.items()}
    finally:
        con.close()

    weather = data["now_weather"][0] if data["now_weather"] else {}
    if weather:
        weather["description"] = WEATHER_CODES.get(weather.get("weather_code"), "Weather")
    data["now_weather"] = weather
    data["now_air"] = data["now_air"][0] if data["now_air"] else {}
    data["now_bikes"] = data["now_bikes"][0] if data["now_bikes"] else {}
    data["coverage"] = data["coverage"][0] if data["coverage"] else {}
    data["line_colours"] = LINE_COLOURS
    data["built_at"] = datetime.now(UTC).isoformat()
    return data


def build_dashboard(db_path: Path, out_dir: Path) -> Path:
    data = collect(db_path)
    template = Template(files("london_pulse").joinpath("templates/dashboard.html").read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_json = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    html = template.render(data_json=safe_json)
    target = out_dir / "index.html"
    target.write_text(html, encoding="utf-8")
    (out_dir / "data.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    log.info("dashboard written to %s", target)
    return target
