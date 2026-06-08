"""Fetch and parse air quality data from the Open-Meteo air quality API."""

from __future__ import annotations

import requests

_BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
_TIMEOUT = 10

_CURRENT_FIELDS = "us_aqi,pm2_5,pm10"

_AQI_CATEGORIES: list[tuple[int, str]] = [
    (50,  "Good"),
    (100, "Moderate"),
    (150, "Unhealthy for Sensitive Groups"),
    (200, "Unhealthy"),
    (300, "Very Unhealthy"),
]


class AirQualityAPIError(Exception):
    """Raised when the air quality API call fails."""


def aqi_label(us_aqi: int) -> str:
    """Map a numeric US AQI value to its human-readable category."""
    for threshold, label in _AQI_CATEGORIES:
        if us_aqi <= threshold:
            return label
    return "Hazardous"


def fetch_air_quality(lat: float, lon: float) -> dict:
    """Fetch current air quality from Open-Meteo.

    Returns a dict with keys:
        us_aqi       — numeric US AQI value
        us_aqi_label — human-readable AQI category string
        pm2_5        — PM2.5 particulate level (μg/m³)
        pm10         — PM10 particulate level (μg/m³)
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": _CURRENT_FIELDS,
        "timezone": "auto",
    }

    try:
        response = requests.get(_BASE_URL, params=params, timeout=_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise AirQualityAPIError(f"Air quality API request failed: {exc}") from exc

    try:
        raw = data["current"]
        aqi_value = raw["us_aqi"]

        return {
            "us_aqi":       aqi_value,
            "us_aqi_label": aqi_label(aqi_value),
            "pm2_5":        raw["pm2_5"],
            "pm10":         raw["pm10"],
        }
    except (KeyError, TypeError) as exc:
        raise AirQualityAPIError(f"Unexpected air quality API response: {exc}") from exc
