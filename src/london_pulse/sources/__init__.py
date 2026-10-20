"""Data sources. Each module exposes a pure `parse(...)` and a `fetch(...)` that calls the API."""

from london_pulse.sources import air_quality, bikepoints, line_status, weather

SOURCES = {
    "tfl_line_status": line_status,
    "tfl_bikepoints": bikepoints,
    "weather": weather,
    "air_quality": air_quality,
}

__all__ = ["SOURCES"]
