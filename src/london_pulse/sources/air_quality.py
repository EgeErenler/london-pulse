"""Current air quality in central London (Open-Meteo Air Quality, no API key needed)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from london_pulse.config import AIR_FIELDS, LONDON_LAT, LONDON_LON, OPEN_METEO_AIR_URL, Settings
from london_pulse.http import get_json

COLUMNS = {
    "captured_at": "datetime64[us, UTC]",
    "observed_at": "datetime64[us, UTC]",
    "european_aqi": "float64",
    "pm2_5": "float64",
    "pm10": "float64",
    "nitrogen_dioxide": "float64",
    "ozone": "float64",
}


def parse(payload: dict[str, Any], captured_at: datetime) -> list[dict[str, Any]]:
    current = payload.get("current") or {}
    if not current:
        return []
    row: dict[str, Any] = {"captured_at": captured_at, "observed_at": current.get("time")}
    for name in AIR_FIELDS:
        row[name] = current.get(name)
    return [row]


def fetch(session: requests.Session, settings: Settings, captured_at: datetime) -> list[dict]:
    params = {
        "latitude": LONDON_LAT,
        "longitude": LONDON_LON,
        "current": ",".join(AIR_FIELDS),
        "timezone": "UTC",
    }
    payload = get_json(session, OPEN_METEO_AIR_URL, params=params, timeout=settings.timeout_seconds)
    return parse(payload, captured_at)
