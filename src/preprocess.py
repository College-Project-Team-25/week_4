import os
import glob
import numpy as np
import pandas as pd
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Turbine MM92 Constants
RATED_POWER_KW = 2050.0
CUT_IN_SPEED_MS = 3.0
RATED_SPEED_MS = 12.5
CUT_OUT_SPEED_MS = 25.0

# 1. Load and process each turbine file
SCADA_COLS = [
    "# Date and time",
    "Wind speed (m/s)",
    "Wind direction (°)",
    "Power (kW)",
    "Nacelle ambient temperature (°C)",
]

files = sorted(glob.glob(os.path.join(DATA_DIR, "Turbine_Data_Kelmarsh_*_2024-*.csv")))
turbine_dfs = []

print("Processing all 6 turbine SCADA files...")
for i, fpath in enumerate(files, start=1):
    print(f"  Cleaning and resampling Turbine {i}...")
    df = pd.read_csv(fpath, skiprows=9, usecols=SCADA_COLS)
    df.columns = ["timestamp", "wind_speed", "wind_direction", "power", "temperature"]

    # Drop blank trailing rows
    df = df.dropna(subset=["timestamp", "wind_speed"]).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Clean signal boundaries
    df["power"] = df["power"].clip(lower=0.0, upper=RATED_POWER_KW)
    df["wind_speed"] = df["wind_speed"].clip(lower=0.0, upper=50.0)

    # Impute missing values
    df["power"] = df["power"].interpolate().bfill()
    df["temperature"] = df["temperature"].interpolate().bfill()
    df["wind_direction"] = df["wind_direction"].interpolate().bfill()

    # Wind vector decomposition
    rad = np.deg2rad(df["wind_direction"].values)
    df["wind_u"] = -df["wind_speed"].values * np.sin(rad)
    df["wind_v"] = -df["wind_speed"].values * np.cos(rad)

    # Resample to 1-hour means
    df = df.set_index("timestamp")
    hourly = df.resample("1h").mean().interpolate().reset_index()

    # Calculate theoretical physical power directly
    ws = hourly["wind_speed"].values
    theo_p = np.zeros_like(ws, dtype=float)
    ramp = (ws >= CUT_IN_SPEED_MS) & (ws < RATED_SPEED_MS)
    theo_p[ramp] = RATED_POWER_KW * np.power((ws[ramp] - CUT_IN_SPEED_MS) / (RATED_SPEED_MS - CUT_IN_SPEED_MS), 3)
    rated = (ws >= RATED_SPEED_MS) & (ws <= CUT_OUT_SPEED_MS)
    theo_p[rated] = RATED_POWER_KW
    hourly["power_theoretical"] = theo_p

    # Add turbine prefix to column names
    prefix = f"t{i}_"
    hourly = hourly.rename(columns={c: f"{prefix}{c}" for c in hourly.columns if c != "timestamp"})
    turbine_dfs.append(hourly)

# 2. Merge all turbines into a single synchronized dataset
print("\nMerging all turbines into farm dataset...")
merged = turbine_dfs[0]
for t_df in turbine_dfs[1:]:
    merged = pd.merge(merged, t_df, on="timestamp", how="inner")

# 3. Add Farm Aggregates
power_cols = [f"t{i}_power" for i in range(1, 7)]
wind_cols = [f"t{i}_wind_speed" for i in range(1, 7)]
theo_cols = [f"t{i}_power_theoretical" for i in range(1, 7)]

merged["farm_total_power"] = merged[power_cols].sum(axis=1)
merged["farm_mean_wind_speed"] = merged[wind_cols].mean(axis=1)
merged["farm_theoretical_power"] = merged[theo_cols].sum(axis=1)

# 4. Cyclical Time Features
hour = merged["timestamp"].dt.hour.values
month = merged["timestamp"].dt.month.values
merged["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
merged["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
merged["month_sin"] = np.sin(2 * np.pi * month / 12.0)
merged["month_cos"] = np.cos(2 * np.pi * month / 12.0)

# 5. Temporal Lag Features
for lag in [1, 2, 24]:
    merged[f"farm_power_lag_{lag}h"] = merged["farm_total_power"].shift(lag)
    merged[f"farm_wind_lag_{lag}h"] = merged["farm_mean_wind_speed"].shift(lag)

merged = merged.dropna().reset_index(drop=True)

# 6. Save Processed Datasets
parquet_path = os.path.join(DATA_DIR, "processed_kelmarsh_hourly.parquet")
csv_path = os.path.join(DATA_DIR, "processed_kelmarsh_hourly.csv")
merged.to_parquet(parquet_path, index=False)
merged.to_csv(csv_path, index=False)
print(f"Saved processed dataset: {len(merged):,} rows, {merged.shape[1]} columns")

print("SCADA preprocessing complete.")

