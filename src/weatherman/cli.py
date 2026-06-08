"""CLI argument parsing and entry point for WeatherMan."""

from __future__ import annotations

import argparse
from typing import Sequence


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
        default=1,
        metavar="N",
        help="Number of forecast days to retrieve (default: 1).",
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
        f'"{args.city}" (units={args.units}, output={args.output})'
    )
