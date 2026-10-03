# PD — Probability of Default

## Dataset

Suggested starting dataset: **Give Me Some Credit**.

Place the downloaded CSV in:

```text
PD/data/raw/
```

The main target in that dataset is commonly represented by `SeriousDlqin2yrs`.

## Notebooks

1. `01_eda.ipynb` — exploratory analysis.
2. `02_data_quality.ipynb` — missing values, outliers and consistency checks.
3. `03_feature_engineering.ipynb` — transformations and derived variables.
4. `04_logistic_pd.ipynb` — interpretable Logistic Regression.
5. `05_xgboost_challenger.ipynb` — nonlinear challenger.
6. `06_validation.ipynb` — discrimination and calibration.
7. `07_monitoring.ipynb` — PSI and risk-band monitoring.

The notebooks contain a generic loading section. Adjust the filename and target if your downloaded dataset differs.
