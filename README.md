# WeatherMan

![Coverage](coverage.svg)

A command-line weather app powered by the [Open-Meteo](https://open-meteo.com/) API — free, no API key required.

---

## Features

- Current conditions: temperature, humidity, wind speed & gusts, precipitation probability, weather description + icon
- Daily forecast up to 7 days: high/low temps, weather description + icon, precipitation probability
- Air quality: US AQI (human-readable), PM2.5, PM10
- Flexible output: JSON (default) or plain text
- Metric or imperial units
- WMO weather interpretation codes mapped to human-readable strings and Unicode icons

---

## Installation

**Requirements:** Python 3.11+

```bash
git clone https://github.com/satsgun/WeatherMan.git
cd WeatherMan
python3 -m venv .venv --without-pip
source .venv/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python
pip install -e .
```

> **Note:** On systems where `python3 -m venv .venv` works (i.e. `python3.X-venv` is installed), you can skip the `--without-pip` / `get-pip.py` steps and run `python3 -m venv .venv && source .venv/bin/activate && pip install -e .` directly.

---

## Usage

```
weatherman --city CITY [--days N] [--units {metric,imperial}] [--output {json,text}]
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--city` | **Yes** | — | City or place name to fetch weather for |
| `--days` | No | `1` | Number of forecast days (1–7) |
| `--units` | No | `metric` | Unit system: `metric` or `imperial` |
| `--output` | No | `json` | Output format: `json` or `text` |

---

## Example Commands

### Basic — current weather for a city
```bash
weatherman --city London
```

### 3-day forecast in imperial units
```bash
weatherman --city "New York" --days 3 --units imperial
```

### 7-day forecast as plain text
```bash
weatherman --city Tokyo --days 7 --output text
```

### Metric units, JSON output (defaults)
```bash
weatherman --city Paris --units metric --output json
```

---

## Output

### JSON (default)
```json
{
  "location": {
    "name": "London",
    "latitude": 51.50853,
    "longitude": -0.12574,
    "altitude": 25.0,
    "timezone": "Europe/London",
    "country": "United Kingdom"
  },
  "current": {
    "temperature_2m": 12.3,
    "relative_humidity_2m": 74,
    "wind_speed_10m": 18.5,
    "wind_gusts_10m": 27.2,
    "precipitation_probability": 40,
    "weather_code": 61,
    "weather_description": "Slight rain",
    "weather_icon": "🌧️"
  },
  "daily": [
    {
      "date": "2024-06-01",
      "temperature_2m_max": 15.1,
      "temperature_2m_min": 9.4,
      "weather_code": 61,
      "weather_description": "Slight rain",
      "weather_icon": "🌧️",
      "precipitation_probability_max": 65
    }
  ],
  "air_quality": {
    "us_aqi": 42,
    "us_aqi_label": "Good",
    "pm2_5": 8.5,
    "pm10": 15.2
  }
}
```

---

## Error Cases

### Missing required argument
```bash
$ weatherman
usage: weatherman [-h] --city CITY [--days N] [--units {metric,imperial}] [--output {json,text}]
weatherman: error: the following arguments are required: --city
# Exit code: 2
```

### Invalid `--days` value (non-integer)
```bash
$ weatherman --city London --days abc
usage: weatherman [-h] --city CITY [--days N] [--units {metric,imperial}] [--output {json,text}]
weatherman: error: argument --days: invalid int value: 'abc'
# Exit code: 2
```

### Invalid `--units` choice
```bash
$ weatherman --city London --units kelvin
usage: weatherman [-h] --city CITY [--days N] [--units {metric,imperial}] [--output {json,text}]
weatherman: error: argument --units: invalid choice: 'kelvin' (choose from 'metric', 'imperial')
# Exit code: 2
```

### Invalid `--output` choice
```bash
$ weatherman --city London --output csv
weatherman: error: argument --output: invalid choice: 'csv' (choose from 'json', 'text')
# Exit code: 2
```

### City not found
```bash
$ weatherman --city Xyzzyville
Error: Could not geocode city: City not found: 'Xyzzyville'
# Exit code: 1
```

### Network error
```bash
$ weatherman --city London
Error: Could not fetch weather: Weather API request failed: ...
# Exit code: 1
```

---

## Development

### Setup
```bash
pip install -e ".[dev]"
```

### Run tests
```bash
pytest
```

### Regenerate coverage badge
```bash
pytest --cov=weatherman --cov-report=xml
genbadge coverage -i coverage.xml -o coverage.svg
```

---

## Data Sources

| Data | API Endpoint |
|---|---|
| Geocoding | [Open-Meteo Geocoding API](https://geocoding-api.open-meteo.com/v1/search) |
| Weather forecast | [Open-Meteo Forecast API](https://api.open-meteo.com/v1/forecast) |
| Air quality | [Open-Meteo Air Quality API](https://air-quality-api.open-meteo.com/v1/air-quality) |

All APIs are free and require no API key.
