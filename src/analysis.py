import os
import pandas as pd

# 1. Load merged dataset
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "merged_turbines_data.csv")
print(f"Loading merged dataset from: {DATA_PATH}\n")
df = pd.read_csv(DATA_PATH)

# 2. Dataset Shape
print("=" * 60)
print("1. DATASET SHAPE")
print("=" * 60)
print(f"Rows: {df.shape[0]:,}, Columns: {df.shape[1]}\n")

# 3. First 5 Rows (Head)
print("=" * 60)
print("2. FIRST 5 ROWS (HEAD)")
print("=" * 60)
print(df.head())
print("\n")

# 4. Last 5 Rows (Tail)
print("=" * 60)
print("3. LAST 5 ROWS (TAIL)")
print("=" * 60)
print(df.tail())
print("\n")

# 5. Dataset Info
print("=" * 60)
print("4. DATASET INFO")
print("=" * 60)
df.info()
print("\n")

# 6. Statistical Description (Describe)
print("=" * 60)
print("5. STATISTICAL DESCRIPTION (DESCRIBE)")
print("=" * 60)
print(df.describe())
print("\n")

# 7. Missing Values
print("=" * 60)
print("6. MISSING VALUES PER COLUMN")
print("=" * 60)
print(df.isnull().sum())
print("\n")

# 8. Turbine Record Counts
print("=" * 60)
print("7. TURBINE RECORD COUNTS")
print("=" * 60)
print(df["turbine"].value_counts())
print("\n")
