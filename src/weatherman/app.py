"""Orchestrate geocoding, weather, and air quality into a single response."""

from __future__ import annotations

from weatherman.geocoder import fetch_geocoding, GeocodingAPIError
from weatherman.weather import fetch_weather, WeatherAPIError
from weatherman.air_quality import fetch_air_quality, AirQualityAPIError


class AppError(Exception):
    """Raised when any step of the end-to-end pipeline fails."""


def get_complete_weather(
    city: str,
    days: int = 1,
    units: str = "metric",
) -> dict:
    """Return complete weather data for *city*.

    Pipeline:
        1. Geocode city → location (lat, lon, altitude, timezone)
        2. Fetch weather forecast (current + daily)
        3. Fetch air quality (US AQI, PM2.5, PM10)

    Returns a dict with keys: location, current, daily, air_quality.
    Raises AppError if any API call fails.
    """
    try:
        location = fetch_geocoding(city)
    except GeocodingAPIError as exc:
        raise AppError(f"Could not geocode city: {exc}") from exc

    lat, lon = location["latitude"], location["longitude"]

    try:
        weather = fetch_weather(lat, lon, days=days, units=units)
    except WeatherAPIError as exc:
        raise AppError(f"Could not fetch weather: {exc}") from exc

    try:
        air_quality = fetch_air_quality(lat, lon)
    except AirQualityAPIError as exc:
        raise AppError(f"Could not fetch air quality: {exc}") from exc

    return {
        "location":    location,
        "current":     weather["current"],
        "daily":       weather["daily"],
        "air_quality": air_quality,
    }
