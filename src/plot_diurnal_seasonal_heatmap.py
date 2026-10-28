import os
import pandas as pd
import matplotlib.pyplot as plt

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed_kelmarsh_hourly.parquet")
CSV_BACKUP = os.path.join(BASE_DIR, "data", "processed_kelmarsh_hourly.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "diurnal_seasonal_heatmap.png")

# Load dataset
if os.path.exists(DATA_PATH):
    df = pd.read_parquet(DATA_PATH)
else:
    df = pd.read_csv(CSV_BACKUP)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["month"] = df["timestamp"].dt.month

# Compute mean power (kW) by month and hour
pivot = df.pivot_table(
    index="month",
    columns="hour",
    values="farm_total_power",
    aggfunc="mean"
)

# Convert to MW for readability
pivot_mw = pivot / 1000.0

# Plotting heatmap
fig, ax = plt.subplots(figsize=(12, 6))
cax = ax.imshow(pivot_mw, cmap="viridis", aspect="auto", origin="lower")

cbar = fig.colorbar(cax, ax=ax)
cbar.set_label("Mean Farm Generation (MW)", fontsize=11)

month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ax.set_yticks(range(len(pivot_mw.index)))
ax.set_yticklabels([month_labels[m - 1] for m in pivot_mw.index])

ax.set_xticks(range(24))
ax.set_xlabel("Hour of Day (UTC)", fontsize=11)
ax.set_ylabel("Month", fontsize=11)
ax.set_title("Kelmarsh Wind Farm: Diurnal and Seasonal Generation Heatmap", fontsize=13, pad=12)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300)
print(f"Heatmap saved to: {OUTPUT_PATH}")

