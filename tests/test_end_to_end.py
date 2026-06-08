"""End-to-end tests: given a city name, complete weather is returned.

Patches weatherman.app.fetch_geocoding / fetch_weather / fetch_air_quality
directly so the orchestration in app.py is exercised without hitting the
network and without the "last patch wins" problem that arises when three
modules all share the same requests.get reference.
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from weatherman.app import get_complete_weather, AppError
from weatherman.geocoder import GeocodingAPIError
from weatherman.weather import WeatherAPIError
from weatherman.air_quality import AirQualityAPIError


# ---------------------------------------------------------------------------
# Canonical mock return values (already-parsed dicts, not HTTP responses)
# ---------------------------------------------------------------------------

GEOCODED_LONDON = {
    "name": "London",
    "latitude": 51.50853,
    "longitude": -0.12574,
    "altitude": 25.0,
    "timezone": "Europe/London",
    "country": "United Kingdom",
}

WEATHER_1DAY = {
    "current": {
        "temperature_2m": 18.5,
        "relative_humidity_2m": 65,
        "wind_speed_10m": 14.0,
        "wind_gusts_10m": 20.5,
        "precipitation_probability": 20,
        "weather_code": 2,
        "weather_description": "Partly cloudy",
        "weather_icon": "⛅",
    },
    "daily": [
        {
            "date": "2024-06-01",
            "temperature_2m_max": 22.0,
            "temperature_2m_min": 13.5,
            "weather_code": 2,
            "weather_description": "Partly cloudy",
            "weather_icon": "⛅",
            "precipitation_probability_max": 25,
        }
    ],
}

WEATHER_7DAY = {
    "current": WEATHER_1DAY["current"],
    "daily": [
        {
            "date": f"2024-06-0{i}",
            "temperature_2m_max": 22.0 - (i - 1),
            "temperature_2m_min": 13.5 - (i - 1),
            "weather_code": [2, 61, 0, 3, 80, 1, 0][i - 1],
            "weather_description": ["Partly cloudy", "Slight rain", "Clear sky",
                                    "Overcast", "Slight rain showers",
                                    "Mainly clear", "Clear sky"][i - 1],
            "weather_icon": ["⛅", "🌧️", "☀️", "☁️", "🌦️", "🌤️", "☀️"][i - 1],
            "precipitation_probability_max": [25, 75, 5, 30, 60, 10, 5][i - 1],
        }
        for i in range(1, 8)
    ],
}

AIR_QUALITY = {
    "us_aqi": 42,
    "us_aqi_label": "Good",
    "pm2_5": 8.5,
    "pm10": 15.2,
}


def _patches(geo=GEOCODED_LONDON, wx=WEATHER_1DAY, aq=AIR_QUALITY):
    """Return a context manager that patches all three app-level callables."""
    from contextlib import ExitStack
    from unittest.mock import patch

    stack = ExitStack()
    mock_geo = stack.enter_context(patch("weatherman.app.fetch_geocoding", return_value=geo))
    mock_wx  = stack.enter_context(patch("weatherman.app.fetch_weather",   return_value=wx))
    mock_aq  = stack.enter_context(patch("weatherman.app.fetch_air_quality", return_value=aq))
    return stack, mock_geo, mock_wx, mock_aq


# ---------------------------------------------------------------------------
# Top-level structure
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherStructure:

    @pytest.fixture
    def result(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            return get_complete_weather("London")

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_location_key(self, result):
        assert "location" in result

    def test_has_current_key(self, result):
        assert "current" in result

    def test_has_daily_key(self, result):
        assert "daily" in result

    def test_has_air_quality_key(self, result):
        assert "air_quality" in result


# ---------------------------------------------------------------------------
# Location data
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherLocation:

    @pytest.fixture
    def result(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            return get_complete_weather("London")

    def test_location_name(self, result):
        assert result["location"]["name"] == "London"

    def test_location_latitude(self, result):
        assert result["location"]["latitude"] == 51.50853

    def test_location_longitude(self, result):
        assert result["location"]["longitude"] == -0.12574

    def test_location_altitude(self, result):
        assert result["location"]["altitude"] == 25.0

    def test_location_timezone(self, result):
        assert result["location"]["timezone"] == "Europe/London"

    def test_location_country(self, result):
        assert result["location"]["country"] == "United Kingdom"


# ---------------------------------------------------------------------------
# Current weather fields
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherCurrentFields:

    @pytest.fixture
    def result(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            return get_complete_weather("London")

    def test_temperature(self, result):
        assert result["current"]["temperature_2m"] == 18.5

    def test_humidity(self, result):
        assert result["current"]["relative_humidity_2m"] == 65

    def test_wind_speed(self, result):
        assert result["current"]["wind_speed_10m"] == 14.0

    def test_wind_gusts(self, result):
        assert result["current"]["wind_gusts_10m"] == 20.5

    def test_precipitation_probability(self, result):
        assert result["current"]["precipitation_probability"] == 20

    def test_weather_code(self, result):
        assert result["current"]["weather_code"] == 2

    def test_weather_description(self, result):
        assert result["current"]["weather_description"] == "Partly cloudy"

    def test_weather_icon(self, result):
        assert result["current"]["weather_icon"] == "⛅"


# ---------------------------------------------------------------------------
# Daily forecast fields
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherDaily:

    @pytest.fixture
    def result_7day(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_7DAY), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            return get_complete_weather("London", days=7)

    def test_daily_is_list(self, result_7day):
        assert isinstance(result_7day["daily"], list)

    def test_daily_has_7_entries(self, result_7day):
        assert len(result_7day["daily"]) == 7

    def test_daily_entry_has_date(self, result_7day):
        assert result_7day["daily"][0]["date"] == "2024-06-01"

    def test_daily_entry_has_max_temp(self, result_7day):
        assert result_7day["daily"][0]["temperature_2m_max"] == 22.0

    def test_daily_entry_has_min_temp(self, result_7day):
        assert result_7day["daily"][0]["temperature_2m_min"] == 13.5

    def test_daily_entry_has_weather_description(self, result_7day):
        assert result_7day["daily"][0]["weather_description"] == "Partly cloudy"

    def test_daily_entry_has_weather_icon(self, result_7day):
        assert result_7day["daily"][0]["weather_icon"] == "⛅"

    def test_daily_entry_has_precipitation_probability(self, result_7day):
        assert result_7day["daily"][0]["precipitation_probability_max"] == 25

    def test_all_daily_entries_have_required_keys(self, result_7day):
        required = {
            "date", "temperature_2m_max", "temperature_2m_min",
            "weather_code", "weather_description", "weather_icon",
            "precipitation_probability_max",
        }
        for entry in result_7day["daily"]:
            assert required <= entry.keys()


# ---------------------------------------------------------------------------
# Air quality fields
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherAirQuality:

    @pytest.fixture
    def result(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            return get_complete_weather("London")

    def test_us_aqi(self, result):
        assert result["air_quality"]["us_aqi"] == 42

    def test_us_aqi_label(self, result):
        assert result["air_quality"]["us_aqi_label"] == "Good"

    def test_pm2_5(self, result):
        assert result["air_quality"]["pm2_5"] == 8.5

    def test_pm10(self, result):
        assert result["air_quality"]["pm10"] == 15.2


# ---------------------------------------------------------------------------
# Orchestration — geocoded coords are forwarded to weather + AQ
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherOrchestration:

    def test_geocoded_lat_lon_passed_to_fetch_weather(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON) as mock_geo, \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY) as mock_wx, \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            get_complete_weather("London")
        mock_wx.assert_called_once()
        args = mock_wx.call_args
        assert args[0][0] == 51.50853   # lat
        assert args[0][1] == -0.12574   # lon

    def test_geocoded_lat_lon_passed_to_fetch_air_quality(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY) as mock_aq:
            get_complete_weather("London")
        mock_aq.assert_called_once()
        args = mock_aq.call_args
        assert args[0][0] == 51.50853
        assert args[0][1] == -0.12574

    def test_days_passed_to_fetch_weather(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_7DAY) as mock_wx, \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            get_complete_weather("London", days=7)
        assert mock_wx.call_args[1]["days"] == 7

    def test_imperial_units_passed_to_fetch_weather(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY) as mock_wx, \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            get_complete_weather("London", units="imperial")
        assert mock_wx.call_args[1]["units"] == "imperial"

    def test_metric_units_passed_to_fetch_weather(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY) as mock_wx, \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            get_complete_weather("London", units="metric")
        assert mock_wx.call_args[1]["units"] == "metric"


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherErrorPropagation:

    def test_geocoding_failure_raises_app_error(self):
        with patch("weatherman.app.fetch_geocoding",
                   side_effect=GeocodingAPIError("unreachable")):
            with pytest.raises(AppError):
                get_complete_weather("London")

    def test_weather_failure_raises_app_error(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",
                   side_effect=WeatherAPIError("unreachable")), \
             patch("weatherman.app.fetch_air_quality", return_value=AIR_QUALITY):
            with pytest.raises(AppError):
                get_complete_weather("London")

    def test_air_quality_failure_raises_app_error(self):
        with patch("weatherman.app.fetch_geocoding", return_value=GEOCODED_LONDON), \
             patch("weatherman.app.fetch_weather",    return_value=WEATHER_1DAY), \
             patch("weatherman.app.fetch_air_quality",
                   side_effect=AirQualityAPIError("unreachable")):
            with pytest.raises(AppError):
                get_complete_weather("London")

    def test_city_not_found_raises_app_error(self):
        with patch("weatherman.app.fetch_geocoding",
                   side_effect=GeocodingAPIError("City not found: 'Xyzzyville'")):
            with pytest.raises(AppError):
                get_complete_weather("Xyzzyville")
