import requests


def get_weather(city):
    """Uses free Open-Meteo geocoding and forecast endpoints; no API key."""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10
        )
        geo.raise_for_status()
        results = geo.json().get("results", [])
        if not results:
            return f"I couldn't find the location {city}."
        place = results[0]
        forecast = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                           "is_day,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto"
            },
            timeout=10
        )
        forecast.raise_for_status()
        current = forecast.json().get("current", {})
        return (
            f"Weather in {place['name']}: {current.get('temperature_2m', 'N/A')}°C, "
            f"feels like {current.get('apparent_temperature', 'N/A')}°C, "
            f"humidity {current.get('relative_humidity_2m', 'N/A')}%, "
            f"wind {current.get('wind_speed_10m', 'N/A')} km/h."
        )
    except requests.RequestException as exc:
        return f"Weather service error: {exc}"
