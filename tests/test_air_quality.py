"""Tests for air quality API fetching, parsing, and AQI label mapping."""

import pytest
from unittest.mock import patch, MagicMock
import requests

from weatherman.air_quality import fetch_air_quality, aqi_label, AirQualityAPIError


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

MOCK_AQ_RESPONSE = {
    "latitude": 51.5,
    "longitude": -0.12,
    "timezone": "Europe/London",
    "current": {
        "time": "2024-01-15T12:00",
        "us_aqi": 42,
        "pm2_5": 8.5,
        "pm10": 15.2,
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
# AQI label mapping
# ---------------------------------------------------------------------------

class TestAqiLabel:

    def test_0_is_good(self):
        assert aqi_label(0) == "Good"

    def test_50_is_good(self):
        assert aqi_label(50) == "Good"

    def test_51_is_moderate(self):
        assert aqi_label(51) == "Moderate"

    def test_100_is_moderate(self):
        assert aqi_label(100) == "Moderate"

    def test_101_is_unhealthy_for_sensitive_groups(self):
        assert aqi_label(101) == "Unhealthy for Sensitive Groups"

    def test_150_is_unhealthy_for_sensitive_groups(self):
        assert aqi_label(150) == "Unhealthy for Sensitive Groups"

    def test_151_is_unhealthy(self):
        assert aqi_label(151) == "Unhealthy"

    def test_200_is_unhealthy(self):
        assert aqi_label(200) == "Unhealthy"

    def test_201_is_very_unhealthy(self):
        assert aqi_label(201) == "Very Unhealthy"

    def test_300_is_very_unhealthy(self):
        assert aqi_label(300) == "Very Unhealthy"

    def test_301_is_hazardous(self):
        assert aqi_label(301) == "Hazardous"

    def test_500_is_hazardous(self):
        assert aqi_label(500) == "Hazardous"

    def test_returns_string(self):
        assert isinstance(aqi_label(42), str)


# ---------------------------------------------------------------------------
# API call parameters
# ---------------------------------------------------------------------------

class TestFetchAirQualityApiCall:

    @patch("weatherman.air_quality.requests.get")
    def test_calls_correct_base_url(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_AQ_RESPONSE)
        fetch_air_quality(51.5, -0.12)
        url = mock_get.call_args[0][0]
        assert "air-quality-api.open-meteo.com/v1/air-quality" in url

    @patch("weatherman.air_quality.requests.get")
    def test_passes_latitude_and_longitude(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_AQ_RESPONSE)
        fetch_air_quality(51.5074, -0.1278)
        params = mock_get.call_args[1]["params"]
        assert params["latitude"] == 51.5074
        assert params["longitude"] == -0.1278

    @patch("weatherman.air_quality.requests.get")
    def test_requests_us_aqi_pm25_pm10(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_AQ_RESPONSE)
        fetch_air_quality(51.5, -0.12)
        params = mock_get.call_args[1]["params"]
        current_fields = params["current"]
        assert "us_aqi" in current_fields
        assert "pm2_5" in current_fields
        assert "pm10" in current_fields


# ---------------------------------------------------------------------------
# Return value
# ---------------------------------------------------------------------------

class TestFetchAirQualityReturnValue:

    @pytest.fixture
    def result(self):
        with patch("weatherman.air_quality.requests.get") as mock_get:
            mock_get.return_value = _mock_get(MOCK_AQ_RESPONSE)
            return fetch_air_quality(51.5, -0.12)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_us_aqi(self, result):
        assert "us_aqi" in result
        assert result["us_aqi"] == 42

    def test_has_us_aqi_label(self, result):
        assert "us_aqi_label" in result
        assert isinstance(result["us_aqi_label"], str)
        assert result["us_aqi_label"]

    def test_aqi_42_label_is_good(self, result):
        assert result["us_aqi_label"] == "Good"

    def test_has_pm2_5(self, result):
        assert "pm2_5" in result
        assert result["pm2_5"] == 8.5

    def test_has_pm10(self, result):
        assert "pm10" in result
        assert result["pm10"] == 15.2

    def test_all_required_keys_present(self, result):
        assert {"us_aqi", "us_aqi_label", "pm2_5", "pm10"} <= result.keys()


class TestFetchAirQualityAqiLabelVariants:
    """us_aqi_label is derived correctly for different AQI values."""

    @pytest.mark.parametrize("aqi,expected_label", [
        (25, "Good"),
        (75, "Moderate"),
        (125, "Unhealthy for Sensitive Groups"),
        (175, "Unhealthy"),
        (250, "Very Unhealthy"),
        (400, "Hazardous"),
    ])
    def test_aqi_label_in_result(self, aqi, expected_label):
        response = {
            **MOCK_AQ_RESPONSE,
            "current": {**MOCK_AQ_RESPONSE["current"], "us_aqi": aqi},
        }
        with patch("weatherman.air_quality.requests.get") as mock_get:
            mock_get.return_value = _mock_get(response)
            result = fetch_air_quality(51.5, -0.12)
        assert result["us_aqi_label"] == expected_label


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestFetchAirQualityErrors:

    @patch("weatherman.air_quality.requests.get")
    def test_http_error_raises_air_quality_api_error(self, mock_get):
        mock_get.return_value = _mock_get({}, status_code=500)
        with pytest.raises(AirQualityAPIError):
            fetch_air_quality(51.5, -0.12)

    @patch("weatherman.air_quality.requests.get")
    def test_connection_error_raises_air_quality_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(AirQualityAPIError):
            fetch_air_quality(51.5, -0.12)

    @patch("weatherman.air_quality.requests.get")
    def test_timeout_raises_air_quality_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(AirQualityAPIError):
            fetch_air_quality(51.5, -0.12)

    @patch("weatherman.air_quality.requests.get")
    def test_error_message_is_informative(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(AirQualityAPIError, match=r"(?i)air quality"):
            fetch_air_quality(51.5, -0.12)
