"""A shared HTTP session with sensible retries for flaky public APIs."""

from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from london_pulse.config import Settings


def build_session(settings: Settings) -> requests.Session:
    retry = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({"User-Agent": settings.user_agent, "Accept": "application/json"})
    return session


def get_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
    timeout: float = 20,
) -> Any:
    response = session.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()
