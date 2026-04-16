"""
weather_client.py — WeatherClient class
Session 08: APIs, HTTP Requests + Environment Variables

What this file is:
  A module that contains ONE class: WeatherClient.
  This is the S7 pattern: one module, one responsibility.
  The class itself is the S5 pattern: class, __init__, instance methods.

Why a class (not functions)?
  Because in production, API clients are always classes.
  The class holds shared configuration (__init__: base URLs, timeout).
  The methods do the individual jobs: geocode, fetch weather.
  main.py creates one instance and calls its methods — separation of concerns.
"""

import requests


# ── Lookup table: weather code → human-readable description ──────────────────
# This lives at module level (not inside the class) because it is constant data.
# Any file that imports this module can use WEATHER_CODES.
WEATHER_CODES = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2:  "Partly cloudy",
    3:  "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    95: "Thunderstorm",
}


class WeatherClient:
    """
    Wraps the Open-Meteo API (https://open-meteo.com/).
    Free to use — no API key required.

    S5 pattern reminder:
      - __init__ stores configuration that every method needs.
      - Each method does ONE job (Single Responsibility).
      - self gives every method access to the shared config.
    """

    # Class-level constants — the API base URLs.
    # They belong to the class (not to any one instance) because they never change.
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL   = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout=10):
        """
        Store configuration that every method will need.

        timeout (int): seconds to wait for a server response before giving up.
        Storing it on self means we set it once here and every method can use it.
        """
        self.timeout = timeout

    # ── Public methods ────────────────────────────────────────────────────────

    def geocode(self, city_name):
        """
        Convert a city name to latitude and longitude.

        Returns a dict with city, country, latitude, longitude.
        Returns None if the city was not found or the request failed.

        Why a separate method?
          The weather endpoint needs coordinates, not city names.
          Splitting geocoding into its own method means we can test it alone,
          reuse it, and replace it later without touching weather logic.
        """
        params = {
            "name":     city_name,
            "count":    1,
            "language": "en",
            "format":   "json",
        }
        try:
            response = requests.get(self.GEOCODING_URL, params=params, timeout=self.timeout)
            response.raise_for_status()   # raises an exception if status is 4xx or 5xx

            results = response.json().get("results")
            if not results:
                return None             # city name did not match anything

            r = results[0]
            return {
                "city":      r["name"],
                "country":   r.get("country", "Unknown"),
                "latitude":  r["latitude"],
                "longitude": r["longitude"],
            }
        except requests.exceptions.RequestException as network_error:
            print(f"[WeatherClient] Network error during geocoding: {network_error}")
            return None

    def get_current_weather(self, latitude, longitude):
        """
        Fetch current weather conditions for a lat/lon pair.

        Returns a dict with temperature, weather code, humidity, wind speed.
        Returns an empty dict {} if the request failed.
        """
        params = {
            "latitude":  latitude,
            "longitude": longitude,
            "current":   "temperature_2m,weathercode,windspeed_10m,relative_humidity_2m",
        }
        try:
            response = requests.get(self.WEATHER_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("current", {})
        except requests.exceptions.RequestException as network_error:
            print(f"[WeatherClient] Network error fetching weather: {network_error}")
            return {}

    def fetch(self, city_name):
        """
        Full pipeline: city name → coordinates → current weather.

        This is the public-facing method that main.py calls.
        It orchestrates geocode() and get_current_weather() in sequence.

        Returns: (location_dict, weather_dict)
          Both are empty / None on failure so the caller can check before using.
        """
        # Input validation — always validate before calling an external API
        if not city_name or not city_name.strip():
            print("[WeatherClient] City name cannot be empty.")
            return None, {}

        location = self.geocode(city_name.strip())
        if not location:
            print(f"[WeatherClient] City not found: '{city_name}'. Check spelling and try again.")
            return None, {}

        weather = self.get_current_weather(location["latitude"], location["longitude"])
        if not weather:
            print("[WeatherClient] Could not retrieve weather data. Try again.")
            return location, {}

        return location, weather
