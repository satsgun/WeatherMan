"""Tests for WMO weather interpretation code mapping."""

from weatherman.wmo_codes import wmo_description, wmo_icon, WMO_CODES


class TestWmoCodeCoverage:
    """Every standard WMO code is present in the lookup table."""

    EXPECTED_CODES = [
        0, 1, 2, 3,           # clear / cloudy
        45, 48,               # fog
        51, 53, 55,           # drizzle
        56, 57,               # freezing drizzle
        61, 63, 65,           # rain
        66, 67,               # freezing rain
        71, 73, 75, 77,       # snow
        80, 81, 82,           # rain showers
        85, 86,               # snow showers
        95, 96, 99,           # thunderstorm
    ]

    def test_all_expected_codes_present(self):
        for code in self.EXPECTED_CODES:
            assert code in WMO_CODES, f"WMO code {code} missing from WMO_CODES"

    def test_every_entry_has_description_and_icon(self):
        for code, (desc, icon) in WMO_CODES.items():
            assert isinstance(desc, str) and desc, f"Code {code}: empty description"
            assert isinstance(icon, str) and icon, f"Code {code}: empty icon"


class TestWmoDescription:

    def test_clear_sky(self):
        assert wmo_description(0) == "Clear sky"

    def test_mainly_clear(self):
        assert wmo_description(1) == "Mainly clear"

    def test_partly_cloudy(self):
        assert wmo_description(2) == "Partly cloudy"

    def test_overcast(self):
        assert wmo_description(3) == "Overcast"

    def test_fog(self):
        assert wmo_description(45) == "Fog"

    def test_depositing_rime_fog(self):
        assert wmo_description(48) == "Depositing rime fog"

    def test_light_drizzle(self):
        assert wmo_description(51) == "Light drizzle"

    def test_moderate_drizzle(self):
        assert wmo_description(53) == "Moderate drizzle"

    def test_dense_drizzle(self):
        assert wmo_description(55) == "Dense drizzle"

    def test_light_freezing_drizzle(self):
        assert wmo_description(56) == "Light freezing drizzle"

    def test_heavy_freezing_drizzle(self):
        assert wmo_description(57) == "Heavy freezing drizzle"

    def test_slight_rain(self):
        assert wmo_description(61) == "Slight rain"

    def test_moderate_rain(self):
        assert wmo_description(63) == "Moderate rain"

    def test_heavy_rain(self):
        assert wmo_description(65) == "Heavy rain"

    def test_light_freezing_rain(self):
        assert wmo_description(66) == "Light freezing rain"

    def test_heavy_freezing_rain(self):
        assert wmo_description(67) == "Heavy freezing rain"

    def test_slight_snowfall(self):
        assert wmo_description(71) == "Slight snowfall"

    def test_moderate_snowfall(self):
        assert wmo_description(73) == "Moderate snowfall"

    def test_heavy_snowfall(self):
        assert wmo_description(75) == "Heavy snowfall"

    def test_snow_grains(self):
        assert wmo_description(77) == "Snow grains"

    def test_slight_rain_showers(self):
        assert wmo_description(80) == "Slight rain showers"

    def test_moderate_rain_showers(self):
        assert wmo_description(81) == "Moderate rain showers"

    def test_violent_rain_showers(self):
        assert wmo_description(82) == "Violent rain showers"

    def test_slight_snow_showers(self):
        assert wmo_description(85) == "Slight snow showers"

    def test_heavy_snow_showers(self):
        assert wmo_description(86) == "Heavy snow showers"

    def test_thunderstorm(self):
        assert wmo_description(95) == "Thunderstorm"

    def test_thunderstorm_slight_hail(self):
        assert wmo_description(96) == "Thunderstorm with slight hail"

    def test_thunderstorm_heavy_hail(self):
        assert wmo_description(99) == "Thunderstorm with heavy hail"

    def test_unknown_code_returns_string(self):
        result = wmo_description(999)
        assert isinstance(result, str) and result

    def test_negative_code_returns_string(self):
        result = wmo_description(-1)
        assert isinstance(result, str) and result


class TestWmoIcon:

    def test_clear_sky_icon(self):
        assert wmo_icon(0) == "☀️"

    def test_mainly_clear_icon(self):
        assert wmo_icon(1) == "🌤️"

    def test_partly_cloudy_icon(self):
        assert wmo_icon(2) == "⛅"

    def test_overcast_icon(self):
        assert wmo_icon(3) == "☁️"

    def test_fog_icon(self):
        assert wmo_icon(45) == "🌫️"

    def test_rain_icon(self):
        assert wmo_icon(61) in ("🌧️", "🌦️")

    def test_snow_icon(self):
        assert wmo_icon(71) == "❄️"

    def test_thunderstorm_icon(self):
        assert wmo_icon(95) == "⛈️"

    def test_unknown_code_returns_string(self):
        result = wmo_icon(999)
        assert isinstance(result, str) and result
