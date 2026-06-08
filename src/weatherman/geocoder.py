"""Geocode a city name to WGS84 coordinates, altitude, and timezone."""

from __future__ import annotations

import requests

_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_TIMEOUT = 10


class GeocodingAPIError(Exception):
    """Raised when geocoding fails or the city is not found."""


def fetch_geocoding(city: str) -> dict:
    """Return location data for the first result matching *city*.

    Returns a dict with keys:
        name, latitude, longitude, altitude, timezone, country
    """
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        response = requests.get(_BASE_URL, params=params, timeout=_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise GeocodingAPIError(f"Geocoding request failed: {exc}") from exc

    results = data.get("results") or []
    if not results:
        raise GeocodingAPIError(f"City not found: {city!r}")

    hit = results[0]
    return {
        "name":      hit["name"],
        "latitude":  hit["latitude"],
        "longitude": hit["longitude"],
        "altitude":  hit.get("elevation", 0.0),
        "timezone":  hit["timezone"],
        "country":   hit.get("country", ""),
    }
