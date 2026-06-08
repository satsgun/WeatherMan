"""CLI argument parsing and entry point for WeatherMan."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from weatherman.app import get_complete_weather, AppError


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse and return validated CLI arguments.

    Pass an explicit list for testing; omit (or pass None) to read sys.argv.
    """
    parser = argparse.ArgumentParser(
        prog="weatherman",
        description="Fetch weather forecasts from the command line.",
    )
    parser.add_argument(
        "--city",
        required=True,
        metavar="CITY",
        help="City or place name to fetch weather for (required).",
    )
    parser.add_argument(
        "--days",
        type=int,
        choices=range(1, 8),
        default=1,
        metavar="N",
        help="Number of forecast days to retrieve, 1-7 (default: 1).",
    )
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Unit system to use (default: metric).",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json).",
    )
    return parser.parse_args(argv)


def main() -> None:
    """Entry point for the weatherman console script."""
    args = parse_args()
    print(
        f"[WeatherMan] Fetching {args.days}-day forecast for "
        f'"{args.city}" (units={args.units}, output={args.output})',
        file=sys.stderr,
    )

    try:
        data = get_complete_weather(args.city, days=args.days, units=args.units)
    except AppError as exc:
        print(f"[WeatherMan] Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data, args.units)


def _print_text(data: dict, units: str) -> None:
    unit_temp = "°C" if units == "metric" else "°F"
    unit_wind = "km/h" if units == "metric" else "mph"

    loc = data["location"]
    cur = data["current"]
    aq = data["air_quality"]

    print(f"\n{loc['name']}, {loc.get('country', '')}")
    print(f"  {cur.get('weather_icon', '')} {cur.get('weather_description', '')}")
    print(f"  Temperature : {cur['temperature_2m']}{unit_temp}")
    print(f"  Humidity    : {cur['relative_humidity_2m']}%")
    print(f"  Wind        : {cur['wind_speed_10m']} {unit_wind}  (gusts {cur['wind_gusts_10m']} {unit_wind})")
    print(f"  Precip prob : {cur['precipitation_probability']}%")
    print(f"  Air quality : {aq['us_aqi_label']} (AQI {aq['us_aqi']})  PM2.5={aq['pm2_5']}  PM10={aq['pm10']}")

    daily = data.get("daily", [])
    if daily:
        print("\n  Forecast:")
        for day in daily:
            print(
                f"    {day['date']}  {day.get('weather_icon', '')} {day.get('weather_description', '')}"
                f"  {day['temperature_2m_max']}/{day['temperature_2m_min']}{unit_temp}"
                f"  {day['precipitation_probability_max']}% precip"
            )
