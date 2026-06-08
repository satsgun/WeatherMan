"""Tests for weather API fetching and parsing."""

import pytest
from unittest.mock import patch, MagicMock
import requests

from weatherman.weather import fetch_weather, WeatherAPIError


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MOCK_WEATHER_RESPONSE_3DAY = {
    "latitude": 51.5,
    "longitude": -0.12,
    "timezone": "Europe/London",
    "current": {
        "time": "2024-01-15T12:00",
        "temperature_2m": 8.5,
        "relative_humidity_2m": 78,
        "wind_speed_10m": 15.2,
        "wind_gusts_10m": 22.1,
        "precipitation_probability": 35,
        "weather_code": 61,
    },
    "daily": {
        "time": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "temperature_2m_max": [10.2, 12.5, 9.8],
        "temperature_2m_min": [4.1, 5.3, 3.7],
        "weather_code": [61, 3, 0],
        "precipitation_probability_max": [70, 20, 5],
    },
}

MOCK_WEATHER_RESPONSE_1DAY = {
    "latitude": 40.71,
    "longitude": -74.01,
    "timezone": "America/New_York",
    "current": {
        "time": "2024-06-01T09:00",
        "temperature_2m": 22.0,
        "relative_humidity_2m": 55,
        "wind_speed_10m": 10.0,
        "wind_gusts_10m": 14.5,
        "precipitation_probability": 10,
        "weather_code": 0,
    },
    "daily": {
        "time": ["2024-06-01"],
        "temperature_2m_max": [26.5],
        "temperature_2m_min": [18.2],
        "weather_code": [0],
        "precipitation_probability_max": [10],
    },
}


def _mock_get(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.side_effect = (
        None
        if status_code == 200
        else requests.exceptions.HTTPError(response=mock_resp)
    )
    return mock_resp


# ---------------------------------------------------------------------------
# API call parameters
# ---------------------------------------------------------------------------

class TestFetchWeatherApiCall:

    @patch("weatherman.weather.requests.get")
    def test_calls_correct_base_url(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12)
        url = mock_get.call_args[0][0]
        assert "api.open-meteo.com/v1/forecast" in url

    @patch("weatherman.weather.requests.get")
    def test_passes_latitude_and_longitude(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5074, -0.1278)
        params = mock_get.call_args[1]["params"]
        assert params["latitude"] == 51.5074
        assert params["longitude"] == -0.1278

    @patch("weatherman.weather.requests.get")
    def test_passes_forecast_days(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_3DAY)
        fetch_weather(51.5, -0.12, days=3)
        params = mock_get.call_args[1]["params"]
        assert params["forecast_days"] == 3

    @patch("weatherman.weather.requests.get")
    def test_default_forecast_days_is_1(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12)
        params = mock_get.call_args[1]["params"]
        assert params["forecast_days"] == 1

    @patch("weatherman.weather.requests.get")
    def test_metric_units_use_celsius(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12, units="metric")
        params = mock_get.call_args[1]["params"]
        assert params["temperature_unit"] == "celsius"

    @patch("weatherman.weather.requests.get")
    def test_imperial_units_use_fahrenheit(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12, units="imperial")
        params = mock_get.call_args[1]["params"]
        assert params["temperature_unit"] == "fahrenheit"

    @patch("weatherman.weather.requests.get")
    def test_metric_units_use_kmh_wind(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12, units="metric")
        params = mock_get.call_args[1]["params"]
        assert params["wind_speed_unit"] == "kmh"

    @patch("weatherman.weather.requests.get")
    def test_imperial_units_use_mph_wind(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12, units="imperial")
        params = mock_get.call_args[1]["params"]
        assert params["wind_speed_unit"] == "mph"

    @patch("weatherman.weather.requests.get")
    def test_requests_required_current_fields(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12)
        params = mock_get.call_args[1]["params"]
        current_fields = params["current"]
        for field in (
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_gusts_10m",
            "precipitation_probability",
            "weather_code",
        ):
            assert field in current_fields, f"Missing current field: {field}"

    @patch("weatherman.weather.requests.get")
    def test_requests_required_daily_fields(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
        fetch_weather(51.5, -0.12)
        params = mock_get.call_args[1]["params"]
        daily_fields = params["daily"]
        for field in (
            "temperature_2m_max",
            "temperature_2m_min",
            "weather_code",
            "precipitation_probability_max",
        ):
            assert field in daily_fields, f"Missing daily field: {field}"


# ---------------------------------------------------------------------------
# Return value — current weather
# ---------------------------------------------------------------------------

class TestFetchWeatherCurrentFields:

    @pytest.fixture
    def result(self):
        with patch("weatherman.weather.requests.get") as mock_get:
            mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_1DAY)
            return fetch_weather(40.71, -74.01)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_current_key(self, result):
        assert "current" in result

    def test_has_daily_key(self, result):
        assert "daily" in result

    def test_current_temperature(self, result):
        assert result["current"]["temperature_2m"] == 22.0

    def test_current_humidity(self, result):
        assert result["current"]["relative_humidity_2m"] == 55

    def test_current_wind_speed(self, result):
        assert result["current"]["wind_speed_10m"] == 10.0

    def test_current_wind_gusts(self, result):
        assert result["current"]["wind_gusts_10m"] == 14.5

    def test_current_precipitation_probability(self, result):
        assert result["current"]["precipitation_probability"] == 10

    def test_current_weather_code(self, result):
        assert result["current"]["weather_code"] == 0

    def test_current_has_weather_description(self, result):
        assert "weather_description" in result["current"]
        assert isinstance(result["current"]["weather_description"], str)
        assert result["current"]["weather_description"]

    def test_current_has_weather_icon(self, result):
        assert "weather_icon" in result["current"]
        assert isinstance(result["current"]["weather_icon"], str)
        assert result["current"]["weather_icon"]

    def test_current_weather_code_0_maps_to_clear_sky(self, result):
        assert result["current"]["weather_description"] == "Clear sky"

    def test_current_weather_code_0_icon_is_sun(self, result):
        assert result["current"]["weather_icon"] == "☀️"


# ---------------------------------------------------------------------------
# Return value — daily forecast
# ---------------------------------------------------------------------------

class TestFetchWeatherDailyFields:

    @pytest.fixture
    def result_3day(self):
        with patch("weatherman.weather.requests.get") as mock_get:
            mock_get.return_value = _mock_get(MOCK_WEATHER_RESPONSE_3DAY)
            return fetch_weather(51.5, -0.12, days=3)

    def test_daily_is_list(self, result_3day):
        assert isinstance(result_3day["daily"], list)

    def test_daily_length_matches_days(self, result_3day):
        assert len(result_3day["daily"]) == 3

    def test_daily_entry_has_date(self, result_3day):
        assert result_3day["daily"][0]["date"] == "2024-01-15"

    def test_daily_entry_has_max_temp(self, result_3day):
        assert result_3day["daily"][0]["temperature_2m_max"] == 10.2

    def test_daily_entry_has_min_temp(self, result_3day):
        assert result_3day["daily"][0]["temperature_2m_min"] == 4.1

    def test_daily_entry_has_weather_code(self, result_3day):
        assert result_3day["daily"][0]["weather_code"] == 61

    def test_daily_entry_has_description(self, result_3day):
        desc = result_3day["daily"][0]["weather_description"]
        assert isinstance(desc, str) and desc

    def test_daily_entry_has_icon(self, result_3day):
        icon = result_3day["daily"][0]["weather_icon"]
        assert isinstance(icon, str) and icon

    def test_daily_entry_has_precipitation_probability(self, result_3day):
        assert result_3day["daily"][0]["precipitation_probability_max"] == 70

    def test_daily_all_entries_have_required_keys(self, result_3day):
        required = {
            "date", "temperature_2m_max", "temperature_2m_min",
            "weather_code", "weather_description", "weather_icon",
            "precipitation_probability_max",
        }
        for entry in result_3day["daily"]:
            assert required <= entry.keys()

    def test_daily_weather_code_3_maps_to_overcast(self, result_3day):
        assert result_3day["daily"][1]["weather_description"] == "Overcast"

    def test_daily_weather_code_0_maps_to_clear_sky(self, result_3day):
        assert result_3day["daily"][2]["weather_description"] == "Clear sky"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestFetchWeatherErrors:

    @patch("weatherman.weather.requests.get")
    def test_http_error_raises_weather_api_error(self, mock_get):
        mock_get.return_value = _mock_get({}, status_code=500)
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_connection_error_raises_weather_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_timeout_raises_weather_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_weather_api_error_message_is_informative(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(WeatherAPIError, match=r"(?i)weather"):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_missing_current_key_raises_weather_api_error(self, mock_get):
        response = {k: v for k, v in MOCK_WEATHER_RESPONSE_1DAY.items() if k != "current"}
        mock_get.return_value = _mock_get(response)
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_missing_current_field_raises_weather_api_error(self, mock_get):
        current = {k: v for k, v in MOCK_WEATHER_RESPONSE_1DAY["current"].items() if k != "temperature_2m"}
        response = {**MOCK_WEATHER_RESPONSE_1DAY, "current": current}
        mock_get.return_value = _mock_get(response)
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_mismatched_daily_array_lengths_raises_weather_api_error(self, mock_get):
        daily = {**MOCK_WEATHER_RESPONSE_1DAY["daily"], "temperature_2m_max": []}
        response = {**MOCK_WEATHER_RESPONSE_1DAY, "daily": daily}
        mock_get.return_value = _mock_get(response)
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)

    @patch("weatherman.weather.requests.get")
    def test_non_dict_payload_raises_weather_api_error(self, mock_get):
        mock_get.return_value = _mock_get(None)
        with pytest.raises(WeatherAPIError):
            fetch_weather(51.5, -0.12)
