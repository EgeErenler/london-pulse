"""Santander Cycles docking stations: bikes and free docks at each station (TfL BikePoint API)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from london_pulse.config import TFL_BASE_URL, Settings
from london_pulse.http import get_json

COLUMNS = {
    "captured_at": "datetime64[us, UTC]",
    "station_id": "string",
    "station_name": "string",
    "lat": "float64",
    "lon": "float64",
    "nb_bikes": "Int64",
    "nb_standard_bikes": "Int64",
    "nb_ebikes": "Int64",
    "nb_empty_docks": "Int64",
    "nb_docks": "Int64",
    "installed": "boolean",
    "locked": "boolean",
}


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_bool(value: Any) -> bool | None:
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return None


def parse(payload: list[dict[str, Any]], captured_at: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for place in payload:
        # TfL sends every count as a string inside a list of key/value pairs.
        props = {p.get("key"): p.get("value") for p in place.get("additionalProperties", [])}
        rows.append(
            {
                "captured_at": captured_at,
                "station_id": place.get("id"),
                "station_name": place.get("commonName"),
                "lat": place.get("lat"),
                "lon": place.get("lon"),
                "nb_bikes": _to_int(props.get("NbBikes")),
                "nb_standard_bikes": _to_int(props.get("NbStandardBikes")),
                "nb_ebikes": _to_int(props.get("NbEBikes")),
                "nb_empty_docks": _to_int(props.get("NbEmptyDocks")),
                "nb_docks": _to_int(props.get("NbDocks")),
                "installed": _to_bool(props.get("Installed")),
                "locked": _to_bool(props.get("Locked")),
            }
        )
    return rows


def fetch(session: requests.Session, settings: Settings, captured_at: datetime) -> list[dict]:
    params = {"app_key": settings.tfl_app_key} if settings.tfl_app_key else None
    payload = get_json(
        session, f"{TFL_BASE_URL}/BikePoint", params=params, timeout=settings.timeout_seconds
    )
    return parse(payload, captured_at)
