"""End-to-end tests: given a city name, complete weather is returned."""

import pytest
from unittest.mock import patch, MagicMock, call
import requests

from weatherman.app import get_complete_weather, AppError


# ---------------------------------------------------------------------------
# Shared mock API payloads
# ---------------------------------------------------------------------------

MOCK_GEOCODING = {
    "results": [{
        "name": "London",
        "latitude": 51.50853,
        "longitude": -0.12574,
        "elevation": 25.0,
        "timezone": "Europe/London",
        "country": "United Kingdom",
        "country_code": "GB",
    }]
}

MOCK_WEATHER_1DAY = {
    "latitude": 51.50853,
    "longitude": -0.12574,
    "timezone": "Europe/London",
    "current": {
        "time": "2024-06-01T12:00",
        "temperature_2m": 18.5,
        "relative_humidity_2m": 65,
        "wind_speed_10m": 14.0,
        "wind_gusts_10m": 20.5,
        "precipitation_probability": 20,
        "weather_code": 2,
    },
    "daily": {
        "time": ["2024-06-01"],
        "temperature_2m_max": [22.0],
        "temperature_2m_min": [13.5],
        "weather_code": [2],
        "precipitation_probability_max": [25],
    },
}

MOCK_WEATHER_7DAY = {
    "latitude": 51.50853,
    "longitude": -0.12574,
    "timezone": "Europe/London",
    "current": {
        "time": "2024-06-01T12:00",
        "temperature_2m": 18.5,
        "relative_humidity_2m": 65,
        "wind_speed_10m": 14.0,
        "wind_gusts_10m": 20.5,
        "precipitation_probability": 20,
        "weather_code": 2,
    },
    "daily": {
        "time": [f"2024-06-0{i}" for i in range(1, 8)],
        "temperature_2m_max": [22.0, 21.0, 19.5, 23.1, 20.0, 18.5, 17.0],
        "temperature_2m_min": [13.5, 12.0, 11.5, 14.0, 13.0, 12.5, 11.0],
        "weather_code": [2, 61, 0, 3, 80, 1, 0],
        "precipitation_probability_max": [25, 75, 5, 30, 60, 10, 5],
    },
}

MOCK_AIR_QUALITY = {
    "latitude": 51.50853,
    "longitude": -0.12574,
    "timezone": "Europe/London",
    "current": {
        "time": "2024-06-01T12:00",
        "us_aqi": 42,
        "pm2_5": 8.5,
        "pm10": 15.2,
    },
}


def _make_mock_get(geo=MOCK_GEOCODING, wx=MOCK_WEATHER_1DAY, aq=MOCK_AIR_QUALITY):
    """Return a side_effect function that dispatches mock responses by URL."""
    def side_effect(url, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        if "geocoding-api" in url:
            mock_resp.json.return_value = geo
        elif "air-quality-api" in url:
            mock_resp.json.return_value = aq
        else:
            mock_resp.json.return_value = wx
        return mock_resp
    return side_effect


# ---------------------------------------------------------------------------
# Top-level structure
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherStructure:

    @pytest.fixture
    def result(self):
        with patch("weatherman.geocoder.requests.get") as geo_get, \
             patch("weatherman.weather.requests.get") as wx_get, \
             patch("weatherman.air_quality.requests.get") as aq_get:
            geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
            wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
            aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
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
        with patch("weatherman.geocoder.requests.get") as geo_get, \
             patch("weatherman.weather.requests.get") as wx_get, \
             patch("weatherman.air_quality.requests.get") as aq_get:
            geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
            wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
            aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
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
        with patch("weatherman.geocoder.requests.get") as geo_get, \
             patch("weatherman.weather.requests.get") as wx_get, \
             patch("weatherman.air_quality.requests.get") as aq_get:
            geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
            wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
            aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
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
        with patch("weatherman.geocoder.requests.get") as geo_get, \
             patch("weatherman.weather.requests.get") as wx_get, \
             patch("weatherman.air_quality.requests.get") as aq_get:
            geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
            wx_get.return_value = _make_mock_response(MOCK_WEATHER_7DAY)
            aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
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
        with patch("weatherman.geocoder.requests.get") as geo_get, \
             patch("weatherman.weather.requests.get") as wx_get, \
             patch("weatherman.air_quality.requests.get") as aq_get:
            geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
            wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
            aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
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
# Units propagation
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherUnits:

    @patch("weatherman.weather.requests.get")
    @patch("weatherman.geocoder.requests.get")
    @patch("weatherman.air_quality.requests.get")
    def test_imperial_units_passed_to_weather(self, aq_get, geo_get, wx_get):
        geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
        wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
        aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
        get_complete_weather("London", units="imperial")
        params = wx_get.call_args[1]["params"]
        assert params["temperature_unit"] == "fahrenheit"
        assert params["wind_speed_unit"] == "mph"

    @patch("weatherman.weather.requests.get")
    @patch("weatherman.geocoder.requests.get")
    @patch("weatherman.air_quality.requests.get")
    def test_metric_units_passed_to_weather(self, aq_get, geo_get, wx_get):
        geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
        wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
        aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
        get_complete_weather("London", units="metric")
        params = wx_get.call_args[1]["params"]
        assert params["temperature_unit"] == "celsius"
        assert params["wind_speed_unit"] == "kmh"


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------

class TestGetCompleteWeatherErrorPropagation:

    @patch("weatherman.geocoder.requests.get")
    def test_geocoding_failure_raises_app_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(AppError):
            get_complete_weather("London")

    @patch("weatherman.weather.requests.get")
    @patch("weatherman.geocoder.requests.get")
    @patch("weatherman.air_quality.requests.get")
    def test_weather_failure_raises_app_error(self, aq_get, geo_get, wx_get):
        geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
        wx_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        aq_get.return_value = _make_mock_response(MOCK_AIR_QUALITY)
        with pytest.raises(AppError):
            get_complete_weather("London")

    @patch("weatherman.weather.requests.get")
    @patch("weatherman.geocoder.requests.get")
    @patch("weatherman.air_quality.requests.get")
    def test_air_quality_failure_raises_app_error(self, aq_get, geo_get, wx_get):
        geo_get.return_value = _make_mock_response(MOCK_GEOCODING)
        wx_get.return_value = _make_mock_response(MOCK_WEATHER_1DAY)
        aq_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(AppError):
            get_complete_weather("London")

    @patch("weatherman.geocoder.requests.get")
    def test_city_not_found_raises_app_error(self, mock_get):
        mock_get.return_value = _make_mock_response({"results": []})
        with pytest.raises(AppError):
            get_complete_weather("Xyzzyville")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_mock_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.side_effect = (
        None
        if status_code == 200
        else requests.exceptions.HTTPError(response=mock_resp)
    )
    return mock_resp
