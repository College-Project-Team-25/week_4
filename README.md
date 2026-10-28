# Kelmarsh Wind Farm 72-Hour Power Forecasting (Group 25)

**Repository**: [https://github.com/orgs/College-Project-Team-25/repositories](https://github.com/orgs/College-Project-Team-25/repositories)  
**Site**: Kelmarsh Wind Farm, Northamptonshire, UK (6 Senvion MM92 Turbines, 12.3 MW Rated)

---

## 1. Project Planning Documents (Completed)
All five formal module planning documents were developed and consolidated:
- **Plan 1 - Project Specifications**: Problem statement, research question, targets, and KPIs.
- **Plan 2 - Project Timeline & Gantt Chart**: 12-week schedule (05-Feb to 13-May) matching module milestone assessments (supervisor meetings, ethics quiz, poster, report submission, and viva).
- **Plan 3 - Data Management Plan**: Detailed metadata, storage, version control, and UH ethical policy answers (GDPR compliance, CC-BY 4.0 licensing, IEC-61400 collection).
- **Plan 4 - Pipeline Workflow**: Ingestion, 3-model architecture (Baseline NN, Hybrid XGBoost, Pre-trained Chronos), tuning, and deployment.
- **Plan 5 - Test Plan**: In/out-of-scope testing, PEP 8 standards, unit tests (pytest), KPI validation, and UAT.
- Consolidated single submission document: `Combined_Project_Plans.txt` (fits within 3 PDF pages).

---

## 2. Datasets Used

> ⚠️ **Raw turbine data files are NOT included in this repository** (each file is ~2.9 GB).
> You must download them manually and place them inside the `data/` folder before running any scripts.

### Dataset 1 — Kelmarsh Wind Farm SCADA Data
- **Source**: Cubico Sustainable Investments via Zenodo
- **📥 Download here**: [https://zenodo.org/records/5841834](https://zenodo.org/records/5841834)
- **How to download**:
  1. Visit the link above
  2. Download all 6 turbine CSV files (`Turbine_Data_Kelmarsh_1_*.csv` through `Turbine_Data_Kelmarsh_6_*.csv`)
  3. Place them inside the `data/` folder of this repo
- **Frequency**: 10-minute intervals for all 6 turbines across 2024
- **Signals**: Wind speed, wind direction, ambient temperature, pitch angle, active power

### Dataset 2 — Open-Meteo UKMO Weather Forecast API
- **Source**: Open-Meteo (free, no API key required)
- **📥 API endpoint**: [https://api.open-meteo.com](https://api.open-meteo.com)
- **How to use**: Run `python src/weather_service.py 0 72` to fetch 72-hour forecasts automatically
- **Coordinates**: Kelmarsh Wind Farm — 52.41° N, -0.95° W
- **Variables**: 100m hub wind speed, direction, temperature, surface pressure, gusts

---

## 3. Code Developed & Executed Today
All Python scripts were written as flat, readable scripts without nested functions:

### A. `src/eda.py`
- Loads required columns from all 6 raw turbine CSV files.
- Adds a `turbine` column labeling `Turbine 1` through `Turbine 6`.
- Merges all turbines into a single consolidated dataset (`data/merged_turbines_data.csv`, 314,407 records).
- Generates descriptive statistics and saves summary report.

### B. `src/analysis.py`
- Loads `data/merged_turbines_data.csv`.
- Inspects dataset shape, `head()`, `tail()`, `info()`, `describe()`, and missing values.
- Confirms zero missing values across wind speed, direction, and power readings.

### C. `src/preprocess.py`
- Cleans sensor boundaries (clips negative power to 0 kW, caps at 2,050 kW).
- Interpolates minor missing values.
- Decomposes wind speed and angle into orthogonal horizontal wind vectors ($u$ and $v$).
- Resamples 10-minute data to 1-hour interval means matching forecast resolutions.
- Computes theoretical aerodynamic power from the Senvion MM92 power curve.
- Computes whole-farm aggregates (`farm_total_power`, `farm_mean_wind_speed`).
- Creates cyclical time features (`hour_sin/cos`, `month_sin/cos`).
- Engineers temporal autoregressive lags ($t-1h, t-2h, t-24h$).
- Saves processed outputs: `data/processed_kelmarsh_hourly.csv` and `.parquet` (8,760 hourly rows, 56 features).

### D. `src/weather_service.py`
- On-demand weather forecast retrieval based on user-requested hour intervals (e.g., `0 2` for next 2h, or `24 48`).
- **Local Daily Caching System**: Automatically caches 24-hour API responses to `data/cached_weather_forecast.csv`.
- Subsequent user requests on the same day reuse local cache, skipping external API calls and saving quota/tokens.
- Formats wind speed in meters per second (`&wind_speed_unit=ms`) matching turbine physical units.

---

## 4. Generated Artifacts and Data Directory
- `data/merged_turbines_data.csv`: Merged raw dataset with turbine identifiers (314,407 rows).
- `data/processed_kelmarsh_hourly.csv`: Synchronized farm hourly feature matrix (8,760 rows, 56 columns).
- `data/processed_kelmarsh_hourly.parquet`: Fast binary format of processed hourly dataset.
- `data/cached_weather_forecast.csv`: Local daily cache for Open-Meteo weather data.
- `data/requested_weather_slice.csv`: Exact user-sliced weather intervals.
- `data/eda_summary.json` & `simple_eda_report.txt`: Automated statistical reports.
- `Combined_Project_Plans.txt`: Ready-to-submit 5 project plans.

---

## 5. Execution Commands
```bash
# 1. Run exploratory data analysis and create merged dataset
python src/eda.py

# 2. Inspect dataset head, info, and statistical distribution
python src/analysis.py

# 3. Run preprocessing pipeline (cleaning, vector engineering, 1h resampling)
python src/preprocess.py

# 4. Fetch weather forecast for requested hour range (e.g. next 2 hours)
python src/weather_service.py 0 2

# 5. Fetch weather forecast interval (e.g. 24 to 48 hours ahead)
python src/weather_service.py 24 48
```
