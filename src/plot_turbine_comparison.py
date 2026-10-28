import os
import pandas as pd
import matplotlib.pyplot as plt

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed_kelmarsh_hourly.parquet")
CSV_BACKUP = os.path.join(BASE_DIR, "data", "processed_kelmarsh_hourly.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "turbine_comparison.png")

# Load dataset
if os.path.exists(DATA_PATH):
    df = pd.read_parquet(DATA_PATH)
else:
    df = pd.read_csv(CSV_BACKUP)

turbines = [f"t{i}" for i in range(1, 7)]
labels = [f"Turbine {i}" for i in range(1, 7)]
power_cols = [f"{t}_power" for t in turbines]

# Convert power values to kW and compute summary metrics
power_data = [df[col].values for col in power_cols]
mean_powers_kw = [df[col].mean() for col in power_cols]

# Create figure with 2 subplots (Boxplot + Mean Generation Bar Chart)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Subplot 1: Distribution boxplot
box = ax1.boxplot(
    power_data,
    tick_labels=labels,
    patch_artist=True,
    showmeans=True,
    meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "red"}
)
for patch in box["boxes"]:
    patch.set_facecolor("#6baed6")

ax1.set_title("Hourly Power Distribution per Turbine", fontsize=12)
ax1.set_ylabel("Power Output (kW)", fontsize=11)
ax1.grid(axis="y", linestyle="--", alpha=0.6)

# Subplot 2: Mean output comparison
bars = ax2.bar(labels, mean_powers_kw, color="#3182bd", edgecolor="black", alpha=0.85)
ax2.set_title("Mean Power Output per Turbine", fontsize=12)
ax2.set_ylabel("Mean Power (kW)", fontsize=11)
ax2.grid(axis="y", linestyle="--", alpha=0.6)

for bar in bars:
    height = bar.get_height()
    ax2.annotate(
        f"{height:.1f}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9
    )

plt.suptitle("Kelmarsh Wind Farm: Inter-Turbine Generation Comparison", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
print(f"Turbine comparison plot saved to: {OUTPUT_PATH}")

