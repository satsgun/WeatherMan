"""Fetch and parse weather data from the Open-Meteo forecast API."""

from __future__ import annotations

import requests

from weatherman.wmo_codes import wmo_description, wmo_icon

_BASE_URL = "https://api.open-meteo.com/v1/forecast"
_TIMEOUT = 10

_CURRENT_FIELDS = ",".join([
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_gusts_10m",
    "precipitation_probability",
    "weather_code",
])

_DAILY_FIELDS = ",".join([
    "temperature_2m_max",
    "temperature_2m_min",
    "weather_code",
    "precipitation_probability_max",
])


class WeatherAPIError(Exception):
    """Raised when the weather API call fails."""


def fetch_weather(
    lat: float,
    lon: float,
    days: int = 1,
    units: str = "metric",
) -> dict:
    """Fetch current conditions and daily forecast from Open-Meteo.

    Returns a dict with keys:
        current  — current weather fields plus weather_description and weather_icon
        daily    — list of per-day dicts, one entry per forecast day
    """
    temp_unit = "celsius" if units == "metric" else "fahrenheit"
    wind_unit = "kmh" if units == "metric" else "mph"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": _CURRENT_FIELDS,
        "daily": _DAILY_FIELDS,
        "forecast_days": days,
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
        "timezone": "auto",
    }

    try:
        response = requests.get(_BASE_URL, params=params, timeout=_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise WeatherAPIError(f"Weather API request failed: {exc}") from exc

    return _parse(data)


def _parse(data: dict) -> dict:
    raw_current = data["current"]
    code = raw_current["weather_code"]

    current = {
        "temperature_2m":           raw_current["temperature_2m"],
        "relative_humidity_2m":     raw_current["relative_humidity_2m"],
        "wind_speed_10m":           raw_current["wind_speed_10m"],
        "wind_gusts_10m":           raw_current["wind_gusts_10m"],
        "precipitation_probability": raw_current["precipitation_probability"],
        "weather_code":             code,
        "weather_description":      wmo_description(code),
        "weather_icon":             wmo_icon(code),
    }

    raw_daily = data["daily"]
    daily = [
        {
            "date":                         raw_daily["time"][i],
            "temperature_2m_max":           raw_daily["temperature_2m_max"][i],
            "temperature_2m_min":           raw_daily["temperature_2m_min"][i],
            "weather_code":                 raw_daily["weather_code"][i],
            "weather_description":          wmo_description(raw_daily["weather_code"][i]),
            "weather_icon":                 wmo_icon(raw_daily["weather_code"][i]),
            "precipitation_probability_max": raw_daily["precipitation_probability_max"][i],
        }
        for i in range(len(raw_daily["time"]))
    ]

    return {"current": current, "daily": daily}
