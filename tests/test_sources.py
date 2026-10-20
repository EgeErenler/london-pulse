from __future__ import annotations

from london_pulse.sources import air_quality, bikepoints, line_status, weather


def test_line_status_one_row_per_status(load_fixture, captured_at):
    rows = line_status.parse(load_fixture("line_status.json"), captured_at)

    assert len(rows) == 4  # bakerloo 1 + district 2 + elizabeth (no statuses) 1
    district = [r for r in rows if r["line_id"] == "district"]
    assert {r["status_severity"] for r in district} == {9, 5}
    assert district[0]["reason"].startswith("District Line")  # whitespace is trimmed


def test_line_status_without_statuses_is_kept(load_fixture, captured_at):
    rows = line_status.parse(load_fixture("line_status.json"), captured_at)

    elizabeth = next(r for r in rows if r["line_id"] == "elizabeth")
    assert elizabeth["status_severity"] is None
    assert elizabeth["reason"] is None


def test_bikepoints_casts_strings_and_handles_blanks(load_fixture, captured_at):
    rows = bikepoints.parse(load_fixture("bikepoints.json"), captured_at)

    first, second = rows
    assert first["nb_bikes"] == 4 and first["nb_ebikes"] == 1
    assert first["installed"] is True and first["locked"] is False
    assert second["nb_bikes"] is None  # empty string from the API
    assert second["locked"] is True


def test_weather_and_air_parse_current_block(captured_at):
    weather_rows = weather.parse(
        {"current": {"time": "2026-10-21T08:00", "temperature_2m": 11.4, "weather_code": 3}},
        captured_at,
    )
    air_rows = air_quality.parse(
        {"current": {"time": "2026-10-21T08:00", "european_aqi": 31, "pm2_5": 7.2}}, captured_at
    )

    assert weather_rows[0]["temperature_c"] == 11.4
    assert air_rows[0]["european_aqi"] == 31
    assert air_rows[0]["ozone"] is None


def test_empty_payloads_return_no_rows(captured_at):
    assert weather.parse({}, captured_at) == []
    assert air_quality.parse({"current": {}}, captured_at) == []
    assert line_status.parse([], captured_at) == []
