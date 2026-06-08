# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in editable mode (run once after cloning)
pip install -e .

# Run all tests with coverage
python -m pytest

# Run a single test file
python -m pytest tests/test_cli.py -v

# Run a single test by name
python -m pytest tests/test_cli.py::TestMain::test_main_json_output_contains_weather_data -v

# Run the CLI
weatherman --city London
weatherman --city "New York" --days 3 --units imperial --output text
```

## Architecture

The app is a thin pipeline: CLI args → geocode city → fetch weather + air quality → print output.

```
cli.py          Parse args, call get_complete_weather(), print JSON or text
app.py          Orchestrate the three API calls into one response dict
geocoder.py     Open-Meteo geocoding API → {name, latitude, longitude, altitude, timezone, country}
weather.py      Open-Meteo forecast API  → {current: {...}, daily: [...]}
air_quality.py  Open-Meteo air quality API → {us_aqi, us_aqi_label, pm2_5, pm10}
wmo_codes.py    WMO weather code → human-readable description + Unicode icon
```

No API key is required — all data comes from [Open-Meteo](https://open-meteo.com/) free APIs.

### Key data contracts

`get_complete_weather(city, days, units)` returns:
```python
{
  "location": {"name", "country", "latitude", "longitude", "altitude", "timezone"},
  "current":  {"temperature_2m", "relative_humidity_2m", "wind_speed_10m",
               "wind_gusts_10m", "precipitation_probability",
               "weather_code", "weather_description", "weather_icon"},
  "daily":    [{"date", "temperature_2m_max", "temperature_2m_min",
                "weather_code", "weather_description", "weather_icon",
                "precipitation_probability_max"}, ...],
  "air_quality": {"us_aqi", "us_aqi_label", "pm2_5", "pm10"},
}
```

### Testing approach

All tests mock at the `requests` level (not at the module boundary) using `monkeypatch`, except CLI tests which mock `weatherman.cli.get_complete_weather` directly. The `--cov` flag runs automatically on every `pytest` invocation.
