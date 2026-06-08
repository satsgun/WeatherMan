"""Tests for weatherman.cli — argument parsing and entry point."""

import json

import pytest
from weatherman.cli import parse_args, main


# ---------------------------------------------------------------------------
# parse_args — valid inputs
# ---------------------------------------------------------------------------

class TestParseArgsValidInputs:

    def test_city_only_sets_all_defaults(self):
        ns = parse_args(["--city", "London"])
        assert ns.city == "London"
        assert ns.days == 1
        assert ns.units == "metric"
        assert ns.output == "json"

    def test_city_with_spaces_preserved(self):
        ns = parse_args(["--city", "New York"])
        assert ns.city == "New York"

    def test_days_override(self):
        ns = parse_args(["--city", "Paris", "--days", "7"])
        assert ns.days == 7

    def test_units_imperial(self):
        ns = parse_args(["--city", "Chicago", "--units", "imperial"])
        assert ns.units == "imperial"

    def test_units_metric_explicit(self):
        ns = parse_args(["--city", "Berlin", "--units", "metric"])
        assert ns.units == "metric"

    def test_output_text(self):
        ns = parse_args(["--city", "Tokyo", "--output", "text"])
        assert ns.output == "text"

    def test_output_json_explicit(self):
        ns = parse_args(["--city", "Oslo", "--output", "json"])
        assert ns.output == "json"

    def test_all_args_together(self):
        ns = parse_args([
            "--city", "Sydney",
            "--days", "3",
            "--units", "imperial",
            "--output", "text",
        ])
        assert ns.city == "Sydney"
        assert ns.days == 3
        assert ns.units == "imperial"
        assert ns.output == "text"


# ---------------------------------------------------------------------------
# parse_args — invalid inputs (argparse exits with code 2)
# ---------------------------------------------------------------------------

class TestParseArgsInvalidInputs:

    def test_missing_city_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args([])
        assert exc_info.value.code == 2

    def test_missing_city_error_mentions_city(self, capsys):
        with pytest.raises(SystemExit):
            parse_args([])
        captured = capsys.readouterr()
        assert "city" in captured.err

    def test_days_non_integer_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--days", "abc"])
        assert exc_info.value.code == 2

    def test_days_float_string_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--days", "2.5"])
        assert exc_info.value.code == 2

    def test_invalid_units_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--units", "kelvin"])
        assert exc_info.value.code == 2

    def test_invalid_output_raises_system_exit(self):
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--city", "London", "--output", "csv"])
        assert exc_info.value.code == 2

    def test_invalid_units_error_mentions_choices(self, capsys):
        with pytest.raises(SystemExit):
            parse_args(["--city", "London", "--units", "kelvin"])
        captured = capsys.readouterr()
        assert "metric" in captured.err or "imperial" in captured.err


# ---------------------------------------------------------------------------
# main — full pipeline
# ---------------------------------------------------------------------------

FAKE_WEATHER = {
    "location": {"name": "London", "country": "GB", "latitude": 51.5, "longitude": -0.1},
    "current": {
        "temperature_2m": 15.0,
        "relative_humidity_2m": 72,
        "wind_speed_10m": 18.0,
        "wind_gusts_10m": 28.0,
        "precipitation_probability": 20,
        "weather_code": 1,
        "weather_description": "Mainly Clear",
        "weather_icon": "🌤",
    },
    "daily": [
        {
            "date": "2026-06-08",
            "temperature_2m_max": 18.0,
            "temperature_2m_min": 11.0,
            "weather_code": 1,
            "weather_description": "Mainly Clear",
            "weather_icon": "🌤",
            "precipitation_probability_max": 10,
        }
    ],
    "air_quality": {
        "us_aqi": 42,
        "us_aqi_label": "Good",
        "pm2_5": 5.1,
        "pm10": 9.3,
    },
}


class TestMain:

    def test_main_json_output_contains_weather_data(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "London"])
        monkeypatch.setattr("weatherman.cli.get_complete_weather", lambda *a, **kw: FAKE_WEATHER)
        main()
        captured = capsys.readouterr()
        assert "temperature_2m" in captured.out
        assert "15.0" in captured.out

    def test_main_json_output_is_valid_json_without_banner(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "London"])
        monkeypatch.setattr("weatherman.cli.get_complete_weather", lambda *a, **kw: FAKE_WEATHER)
        main()
        captured = capsys.readouterr()
        assert json.loads(captured.out) == FAKE_WEATHER
        assert "[WeatherMan] Fetching" not in captured.out
        assert "[WeatherMan] Fetching" in captured.err

    def test_main_calls_pipeline_with_correct_args(self, monkeypatch):
        calls = []
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "Berlin", "--days", "5", "--units", "imperial"])
        monkeypatch.setattr(
            "weatherman.cli.get_complete_weather",
            lambda city, days, units: calls.append((city, days, units)) or FAKE_WEATHER,
        )
        main()
        assert calls == [("Berlin", 5, "imperial")]

    def test_main_text_output_contains_weather_data(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "London", "--output", "text"])
        monkeypatch.setattr("weatherman.cli.get_complete_weather", lambda *a, **kw: FAKE_WEATHER)
        main()
        captured = capsys.readouterr()
        assert "15.0" in captured.out
        assert "Mainly Clear" in captured.out
        assert "Good" in captured.out

    def test_main_text_output_shows_forecast(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "London", "--output", "text", "--days", "3"])
        monkeypatch.setattr("weatherman.cli.get_complete_weather", lambda *a, **kw: FAKE_WEATHER)
        main()
        captured = capsys.readouterr()
        assert "2026-06-08" in captured.out
        assert "18.0" in captured.out

    def test_main_text_output_omits_dangling_comma_when_country_missing(self, capsys, monkeypatch):
        weather_without_country = {**FAKE_WEATHER, "location": {**FAKE_WEATHER["location"], "country": ""}}
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "London", "--output", "text"])
        monkeypatch.setattr("weatherman.cli.get_complete_weather", lambda *a, **kw: weather_without_country)
        main()
        captured = capsys.readouterr()
        assert "\nLondon\n" in captured.out
        assert "London," not in captured.out

    def test_main_exits_nonzero_on_app_error(self, monkeypatch):
        from weatherman.app import AppError
        monkeypatch.setattr("sys.argv", ["weatherman", "--city", "Nowhere"])
        monkeypatch.setattr("weatherman.cli.get_complete_weather", lambda *a, **kw: (_ for _ in ()).throw(AppError("geocode failed")))
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_main_exits_nonzero_on_missing_city(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["weatherman"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code != 0
