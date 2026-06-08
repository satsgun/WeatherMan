"""Tests for city-name geocoding via Open-Meteo geocoding API."""

import pytest
from unittest.mock import patch, MagicMock
import requests

from weatherman.geocoder import fetch_geocoding, GeocodingAPIError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_GEOCODING_RESPONSE = {
    "results": [
        {
            "id": 2643743,
            "name": "London",
            "latitude": 51.50853,
            "longitude": -0.12574,
            "elevation": 25.0,
            "timezone": "Europe/London",
            "country": "United Kingdom",
            "country_code": "GB",
        }
    ]
}

MOCK_GEOCODING_RESPONSE_NO_RESULTS = {
    "results": []
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

class TestFetchGeocodingApiCall:

    @patch("weatherman.geocoder.requests.get")
    def test_calls_correct_base_url(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE)
        fetch_geocoding("London")
        url = mock_get.call_args[0][0]
        assert "geocoding-api.open-meteo.com/v1/search" in url

    @patch("weatherman.geocoder.requests.get")
    def test_passes_city_name(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE)
        fetch_geocoding("London")
        params = mock_get.call_args[1]["params"]
        assert params["name"] == "London"

    @patch("weatherman.geocoder.requests.get")
    def test_requests_single_result(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE)
        fetch_geocoding("London")
        params = mock_get.call_args[1]["params"]
        assert params["count"] == 1

    @patch("weatherman.geocoder.requests.get")
    def test_city_name_with_spaces(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE)
        fetch_geocoding("New York")
        params = mock_get.call_args[1]["params"]
        assert params["name"] == "New York"


# ---------------------------------------------------------------------------
# Return value
# ---------------------------------------------------------------------------

class TestFetchGeocodingReturnValue:

    @pytest.fixture
    def result(self):
        with patch("weatherman.geocoder.requests.get") as mock_get:
            mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE)
            return fetch_geocoding("London")

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_has_name(self, result):
        assert result["name"] == "London"

    def test_has_latitude(self, result):
        assert result["latitude"] == 51.50853

    def test_has_longitude(self, result):
        assert result["longitude"] == -0.12574

    def test_has_altitude(self, result):
        assert result["altitude"] == 25.0

    def test_has_timezone(self, result):
        assert result["timezone"] == "Europe/London"

    def test_has_country(self, result):
        assert result["country"] == "United Kingdom"

    def test_all_required_keys_present(self, result):
        assert {"name", "latitude", "longitude", "altitude", "timezone", "country"} <= result.keys()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestFetchGeocodingErrors:

    @patch("weatherman.geocoder.requests.get")
    def test_city_not_found_raises_geocoding_error(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE_NO_RESULTS)
        with pytest.raises(GeocodingAPIError):
            fetch_geocoding("Xyzzyville")

    @patch("weatherman.geocoder.requests.get")
    def test_city_not_found_error_mentions_city(self, mock_get):
        mock_get.return_value = _mock_get(MOCK_GEOCODING_RESPONSE_NO_RESULTS)
        with pytest.raises(GeocodingAPIError, match="Xyzzyville"):
            fetch_geocoding("Xyzzyville")

    @patch("weatherman.geocoder.requests.get")
    def test_http_error_raises_geocoding_error(self, mock_get):
        mock_get.return_value = _mock_get({}, status_code=500)
        with pytest.raises(GeocodingAPIError):
            fetch_geocoding("London")

    @patch("weatherman.geocoder.requests.get")
    def test_connection_error_raises_geocoding_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("unreachable")
        with pytest.raises(GeocodingAPIError):
            fetch_geocoding("London")

    @patch("weatherman.geocoder.requests.get")
    def test_timeout_raises_geocoding_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(GeocodingAPIError):
            fetch_geocoding("London")

    @patch("weatherman.geocoder.requests.get")
    def test_missing_required_field_raises_geocoding_error(self, mock_get):
        hit = {k: v for k, v in MOCK_GEOCODING_RESPONSE["results"][0].items() if k != "latitude"}
        response = {"results": [hit]}
        mock_get.return_value = _mock_get(response)
        with pytest.raises(GeocodingAPIError):
            fetch_geocoding("London")

    @patch("weatherman.geocoder.requests.get")
    def test_non_dict_result_raises_geocoding_error(self, mock_get):
        mock_get.return_value = _mock_get({"results": ["not-a-dict"]})
        with pytest.raises(GeocodingAPIError):
            fetch_geocoding("London")
