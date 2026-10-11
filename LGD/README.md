# LGD — Loss Given Default

## Objective

Develop an educational Loss Given Default (LGD) workflow using a small public, anonymized loan dataset with observed recovery/LGD fields. This is a portfolio exercise, not a production or regulatory model.

## Dataset

Initial dataset candidate: **LGD dataset** in the public Credit-Scoring-Data-Sets repository.

- [Dataset description](https://github.com/JLZml/Credit-Scoring-Data-Sets/blob/master/6.%20Credit%20risk%20analysis/LGD/data%20description)
- [CSV file](https://github.com/JLZml/Credit-Scoring-Data-Sets/blob/master/6.%20Credit%20risk%20analysis/LGD/lgd.csv)
- The published description reports 2,545 anonymized loan observations provided by a European bank.

The documented fields include `LTV`, `Recovery_rate`, `lgd_time`, `y_logistic`, `lnrr`, `Y_probit`, `purpose1`, and `event`. The first EDA notebook must verify the actual schema, units, target definition, missing values, and value ranges before modelling.

## Target and leakage controls

- Candidate target: `lgd_time`, only after verifying its meaning and scale from the dataset documentation and CSV.
- `Recovery_rate` is mathematically related to LGD; do not use it as a predictor when predicting LGD.
- `y_logistic`, `lnrr`, and `Y_probit` are transformations of the target/recovery and must be excluded from the feature matrix.
- Decide whether `event` is available at the intended prediction time before including it as a predictor.
- Do not manufacture targets or report model metrics before running the notebooks.

## Planned workflow

| Notebook | Purpose |
|---|---|
| `01_eda.ipynb` | Inspect schema, LGD distribution, missingness, bounds and relationships |
| `02_data_quality.ipynb` | Check duplicates, invalid ranges, missingness and target consistency |
| `03_feature_engineering.ipynb` | Define leakage-safe predictors and train/test split |
| `04_lgd_model.ipynb` | Fit a baseline and compare regression challengers |
| `05_validation.ipynb` | Evaluate MAE, RMSE, R², residuals and bounded predictions |
| `06_monitoring.ipynb` | Check sample stability and document limits of temporal inference |

## Methodology principles

- Split data before fitting preprocessing steps.
- Start with a naive/mean baseline before a more complex model.
- Report MAE and RMSE; interpret R² cautiously because the sample is small.
- LGD should be bounded between 0 and 1 (or 0% and 100%). Assess prediction bounds and document any correction or bounded-model approach.
- Use cross-validation or repeated validation where suitable; avoid overclaiming generalization from 2,545 observations.
- Clearly distinguish sample stability from genuine out-of-time monitoring.

## Data handling

Download the CSV from the source above and save it locally as:

`LGD/data/raw/lgd.csv`

Raw and processed data must remain excluded from Git version control. Do not commit credentials, personal data, or confidential banking data.

## Limitations

The public data is small, anonymized and may not represent the user's target portfolio. A production IFRS 9 LGD framework would require institution-specific target definitions, recovery cash flows and costs, discounting, workout timing, segmentation, representativeness checks, forward-looking adjustments where relevant, independent validation, governance and monitoring.

This module will document assumptions and results as they are verified; no unexecuted metrics will be presented as completed findings.
