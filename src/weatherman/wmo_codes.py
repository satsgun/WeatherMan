"""WMO Weather Interpretation Code mapping to descriptions and Unicode icons."""

from __future__ import annotations

WMO_CODES: dict[int, tuple[str, str]] = {
    0:  ("Clear sky",                        "☀️"),
    1:  ("Mainly clear",                     "🌤️"),
    2:  ("Partly cloudy",                    "⛅"),
    3:  ("Overcast",                         "☁️"),
    45: ("Fog",                              "🌫️"),
    48: ("Depositing rime fog",              "🌫️"),
    51: ("Light drizzle",                    "🌦️"),
    53: ("Moderate drizzle",                 "🌦️"),
    55: ("Dense drizzle",                    "🌧️"),
    56: ("Light freezing drizzle",           "🌨️"),
    57: ("Heavy freezing drizzle",           "🌨️"),
    61: ("Slight rain",                      "🌧️"),
    63: ("Moderate rain",                    "🌧️"),
    65: ("Heavy rain",                       "🌧️"),
    66: ("Light freezing rain",              "🌨️"),
    67: ("Heavy freezing rain",              "🌨️"),
    71: ("Slight snowfall",                  "❄️"),
    73: ("Moderate snowfall",                "❄️"),
    75: ("Heavy snowfall",                   "❄️"),
    77: ("Snow grains",                      "🌨️"),
    80: ("Slight rain showers",              "🌦️"),
    81: ("Moderate rain showers",            "🌧️"),
    82: ("Violent rain showers",             "⛈️"),
    85: ("Slight snow showers",              "🌨️"),
    86: ("Heavy snow showers",               "🌨️"),
    95: ("Thunderstorm",                     "⛈️"),
    96: ("Thunderstorm with slight hail",    "⛈️"),
    99: ("Thunderstorm with heavy hail",     "⛈️"),
}

_UNKNOWN: tuple[str, str] = ("Unknown condition", "❓")


def wmo_description(code: int) -> str:
    return WMO_CODES.get(code, _UNKNOWN)[0]


def wmo_icon(code: int) -> str:
    return WMO_CODES.get(code, _UNKNOWN)[1]
