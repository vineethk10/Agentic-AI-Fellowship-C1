"""
result_saver.py — ResultSaver class
Session 08: APIs, HTTP Requests + Environment Variables

What this file is:
  A module with ONE class: ResultSaver.
  It handles saving API results to a JSON file.

S6 connection (File Handling + Data Formats):
  You already know how to read and write JSON files.
  Today we wrap that knowledge in a class so it is reusable across sessions.

S5 connection (OOP):
  __init__ takes the filepath once — every method can then use self.filepath.
  We don't pass the filepath to every method call. We set it once, use it everywhere.
"""

import json
import os
from datetime import datetime


class ResultSaver:
    """
    Saves weather API results to a JSON file.

    Each call to save() APPENDS a new record — it never overwrites existing data.
    This is the correct pattern: preserve history, don't destroy it.
    """

    def __init__(self, filepath):
        """
        Store the output filepath.
        Every method that reads or writes uses self.filepath — set it once here.
        """
        self.filepath = filepath

    def save(self, location, weather, weather_codes):
        """
        Append one weather result to the JSON file.

        Steps (same S6 pattern you already know):
          1. Build a dict for this result.
          2. Read the existing file (if it exists) to get previous records.
          3. Append the new record to the list.
          4. Write the updated list back to the file.

        Returns the saved record dict.
        """
        # Step 1 — build the record
        record = {
            "timestamp":     datetime.now().isoformat(),
            "city":          location["city"],
            "country":       location["country"],
            "temperature_c": weather.get("temperature_2m", "N/A"),
            "condition":     weather_codes.get(weather.get("weathercode", -1), "Unknown"),
            "humidity_pct":  weather.get("relative_humidity_2m", "N/A"),
            "wind_kmh":      weather.get("windspeed_10m", "N/A"),
        }

        # Step 2 — load existing records (or start with an empty list)
        records = self._load_existing()

        # Step 3 — append
        records.append(record)

        # Step 4 — write back
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        print(f"[ResultSaver] Saved to {self.filepath} ({len(records)} record(s) total)")
        return record

    def load_all(self):
        """
        Read all saved results from the JSON file.
        Returns a list of dicts. Returns [] if the file does not exist yet.
        """
        return self._load_existing()

    # ── Private helper ────────────────────────────────────────────────────────

    def _load_existing(self):
        """
        Read the JSON file and return the list of records.
        Returns [] if the file does not exist or is empty/corrupted.

        The leading underscore (_) is a Python convention meaning:
        'this method is for internal use by this class — callers should not call it directly.'
        You will see this pattern in every professional Python codebase.
        """
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []  # file was empty or corrupted — start fresh
