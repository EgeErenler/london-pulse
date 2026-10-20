"""Current weather in central London (Open-Meteo, no API key needed)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from london_pulse.config import (
    LONDON_LAT,
    LONDON_LON,
    OPEN_METEO_WEATHER_URL,
    WEATHER_FIELDS,
    Settings,
)
from london_pulse.http import get_json

COLUMNS = {
    "captured_at": "datetime64[us, UTC]",
    "observed_at": "datetime64[us, UTC]",
    "temperature_c": "float64",
    "apparent_temperature_c": "float64",
    "precipitation_mm": "float64",
    "rain_mm": "float64",
    "cloud_cover_pct": "float64",
    "wind_speed_kmh": "float64",
    "weather_code": "Int64",
}


def parse(payload: dict[str, Any], captured_at: datetime) -> list[dict[str, Any]]:
    current = payload.get("current") or {}
    if not current:
        return []
    return [
        {
            "captured_at": captured_at,
            "observed_at": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "precipitation_mm": current.get("precipitation"),
            "rain_mm": current.get("rain"),
            "cloud_cover_pct": current.get("cloud_cover"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
        }
    ]


def fetch(session: requests.Session, settings: Settings, captured_at: datetime) -> list[dict]:
    params = {
        "latitude": LONDON_LAT,
        "longitude": LONDON_LON,
        "current": ",".join(WEATHER_FIELDS),
        "timezone": "UTC",
    }
    payload = get_json(
        session, OPEN_METEO_WEATHER_URL, params=params, timeout=settings.timeout_seconds
    )
    return parse(payload, captured_at)
