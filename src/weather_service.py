import os
import sys
import numpy as np
import pandas as pd
import requests

LAT = 52.41
LON = -0.95
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CACHE_FILE = os.path.join(DATA_DIR, "cached_weather_forecast.csv")

# 1. Parse user requested hour range
start_hour = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end_hour = int(sys.argv[2]) if len(sys.argv) > 2 else 2
print(f"User requested window: hour {start_hour} to {end_hour}")

# 2. Check if valid local cache already exists for today
full_df = None
today_str = pd.Timestamp.now().strftime("%Y-%m-%d")

if os.path.exists(CACHE_FILE):
    cached = pd.read_csv(CACHE_FILE)
    cached["timestamp"] = pd.to_datetime(cached["timestamp"])
    # Check if cache is from today and covers the requested hours
    if len(cached) >= end_hour and cached["timestamp"].iloc[0].strftime("%Y-%m-%d") == today_str:
        print("Found valid cache for today. Skipping API call!")
        full_df = cached

# 3. If no valid cache, call the API and save to cache
if full_df is None:
    needed_days = max(1, int(np.ceil(end_hour / 24.0)))
    needed_days = min(needed_days, 3)
    print(f"Calling Open-Meteo API for {needed_days} day(s)...")

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
        f"&hourly=temperature_2m,surface_pressure,wind_speed_100m,wind_direction_100m,wind_gusts_10m"
        f"&wind_speed_unit=ms&forecast_days={needed_days}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    payload = resp.json()["hourly"]

    full_df = pd.DataFrame({
        "timestamp": pd.to_datetime(payload["time"]),
        "temp": payload["temperature_2m"],
        "pressure": payload["surface_pressure"],
        "wind_speed": payload["wind_speed_100m"],
        "wind_direction": payload["wind_direction_100m"],
        "gusts": payload["wind_gusts_10m"],
    })
    full_df.to_csv(CACHE_FILE, index=False)
    print(f"Cached {len(full_df)} hours to: {CACHE_FILE}")

# 4. Slice ONLY user requested interval
requested_df = full_df.iloc[start_hour:end_hour].copy()

# 5. Compute theoretical power and wind vectors
ws = requested_df["wind_speed"].values
theo_p = np.zeros_like(ws, dtype=float)
ramp = (ws >= 3.0) & (ws < 12.5)
theo_p[ramp] = 2050.0 * np.power((ws[ramp] - 3.0) / 9.5, 3)
rated = (ws >= 12.5) & (ws <= 25.0)
theo_p[rated] = 2050.0
requested_df["theoretical_power"] = theo_p

rad = np.deg2rad(requested_df["wind_direction"].values)
requested_df["wind_u"] = -ws * np.sin(rad)
requested_df["wind_v"] = -ws * np.cos(rad)

# 6. Save requested slice
out_path = os.path.join(DATA_DIR, "requested_weather_slice.csv")
requested_df.to_csv(out_path, index=False)

print(f"\nReturned {len(requested_df)} hour(s):")
print(requested_df[["timestamp", "wind_speed", "wind_direction", "theoretical_power"]])
