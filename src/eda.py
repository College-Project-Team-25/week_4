import os
import glob
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

COLS = [
    "# Date and time",
    "Wind speed (m/s)",
    "Wind direction (°)",
    "Power (kW)",
    "Nacelle ambient temperature (°C)",
]

# 1. Read and merge all 6 turbine CSV files
files = sorted(glob.glob(os.path.join(DATA_DIR, "Turbine_Data_Kelmarsh_*_2024-*.csv")))
all_dfs = []

for i, f in enumerate(files, start=1):
    print(f"Reading Turbine {i}...")
    df = pd.read_csv(f, skiprows=9, usecols=COLS)
    df.columns = ["date_time", "wind_speed", "wind_direction", "power", "temperature"]
    df = df.dropna(subset=["date_time", "wind_speed"]).copy()
    df["turbine"] = f"Turbine {i}"
    all_dfs.append(df)

merged_df = pd.concat(all_dfs, ignore_index=True)

# 2. Save merged dataset
out_file = os.path.join(DATA_DIR, "merged_turbines_data.csv")
merged_df.to_csv(out_file, index=False)
print(f"\nSaved merged data to: {out_file} ({len(merged_df):,} rows)")

# 3. Simple EDA summary
print("\n--- DATASET SUMMARY ---")
print(f"Shape: {merged_df.shape}")
print("\nMissing Values:")
print(merged_df.isnull().sum())
print("\nAverage Values by Turbine:")
print(merged_df.groupby("turbine")[["wind_speed", "power", "temperature"]].mean())
