"""Central settings. Everything can be overridden with environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Central London (Charing Cross), the usual reference point for "London".
LONDON_LAT = 51.5072
LONDON_LON = -0.1276

TFL_BASE_URL = "https://api.tfl.gov.uk"
TFL_MODES = ("tube", "overground", "dlr", "elizabeth-line")

OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

WEATHER_FIELDS = (
    "temperature_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "cloud_cover",
    "wind_speed_10m",
    "weather_code",
)
AIR_FIELDS = ("european_aqi", "pm2_5", "pm10", "nitrogen_dioxide", "ozone")


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("LP_DATA_DIR", "data")))
    tfl_app_key: str | None = field(default_factory=lambda: os.getenv("TFL_APP_KEY") or None)
    timeout_seconds: float = float(os.getenv("LP_HTTP_TIMEOUT", "20"))
    user_agent: str = "london-pulse/0.1 (+https://github.com/EgeErenler/london-pulse)"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"
