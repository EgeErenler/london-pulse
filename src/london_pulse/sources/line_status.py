"""Live status of Tube, Overground, DLR and Elizabeth line services (TfL Unified API)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from london_pulse.config import TFL_BASE_URL, TFL_MODES, Settings
from london_pulse.http import get_json

COLUMNS = {
    "captured_at": "datetime64[us, UTC]",
    "line_id": "string",
    "line_name": "string",
    "mode": "string",
    "status_severity": "Int64",
    "status_description": "string",
    "reason": "string",
}


def parse(payload: list[dict[str, Any]], captured_at: datetime) -> list[dict[str, Any]]:
    """One row per line status. A line can report more than one status at the same time."""
    rows: list[dict[str, Any]] = []
    for line in payload:
        statuses = line.get("lineStatuses") or [{}]
        for status in statuses:
            rows.append(
                {
                    "captured_at": captured_at,
                    "line_id": line.get("id"),
                    "line_name": line.get("name"),
                    "mode": line.get("modeName"),
                    "status_severity": status.get("statusSeverity"),
                    "status_description": status.get("statusSeverityDescription"),
                    "reason": (status.get("reason") or "").strip() or None,
                }
            )
    return rows


def fetch(session: requests.Session, settings: Settings, captured_at: datetime) -> list[dict]:
    params = {"app_key": settings.tfl_app_key} if settings.tfl_app_key else None
    url = f"{TFL_BASE_URL}/Line/Mode/{','.join(TFL_MODES)}/Status"
    payload = get_json(session, url, params=params, timeout=settings.timeout_seconds)
    return parse(payload, captured_at)
