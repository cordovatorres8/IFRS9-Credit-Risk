# Probability of Default (PD) Modeling

## Overview

This module develops a Probability of Default (PD) modeling framework as part of an educational IFRS 9 Credit Risk project.

The objective is to estimate the probability that a borrower will experience a serious delinquency event within a defined prediction horizon.

The modeling workflow follows a credit risk development process including:

- Exploratory Data Analysis (EDA)
- Data quality assessment
- Feature engineering
- Interpretable baseline modeling
- Challenger model development
- Model validation
- Calibration assessment
- Population Stability Index (PSI) monitoring

---

## Dataset

The modeling exercise uses the public **Give Me Some Credit** dataset.

The dataset contains borrower-level credit information and the target variable:

`SeriousDlqin2yrs`

where:

- `1` = serious delinquency within two years
- `0` = no serious delinquency within two years

The original dataset contains 150,000 observations.

The overall default rate is approximately **6.68%**.

Raw and processed datasets are excluded from version control through `.gitignore`.

---

## Modeling Strategy

Two models were developed:

### 1. Logistic Regression — Champion

Logistic Regression was selected as the champion model because of its:

- Interpretability
- Transparency
- Suitability for credit risk applications
- Ease of explaining the relationship between predictors and default probability

The model was developed using leakage-safe feature engineering, where transformation parameters were estimated exclusively using the training sample.

### 2. XGBoost — Challenger

XGBoost was developed as a challenger model to evaluate whether a nonlinear machine learning approach could improve predictive performance.

The challenger model provides higher discriminatory power while being less interpretable than Logistic Regression.

---

## Data Split

The dataset was divided using a stratified train-test split:

| Sample | Observations |
|---|---:|
| Training | 120,000 |
| Test | 30,000 |

The default rate remained approximately **6.68%** in both samples.

---

## Features

The final leakage-safe modeling dataset contains 14 features, including:

- Age
- Debt ratio
- Credit utilization
- Monthly income
- Number of dependents
- Open credit lines and loans
- Real estate loans
- Total late payments
- Maximum late payment count
- 90+ days past due indicator
- Any late payment indicator
- Late payment severity
- Late payment burden
- Income per credit line

---

## Model Performance

Performance was evaluated using AUC-ROC, Gini coefficient and Kolmogorov-Smirnov (KS) statistic.

| Model | AUC | Gini | KS |
|---|---:|---:|---:|
| Logistic Regression | 0.8628 | 0.7257 | 0.5685 |
| XGBoost | 0.8700 | 0.7401 | 0.5835 |

XGBoost achieved slightly higher predictive performance across all three discrimination metrics.

However, the improvement was moderate, while Logistic Regression provides substantially greater interpretability.

Therefore:

> **Logistic Regression is retained as the champion model, while XGBoost is retained as the challenger.**

---

## Calibration

Model calibration was evaluated using:

- Brier score
- Calibration curves
- Predicted versus observed default rates by decile

### Brier Score

| Model | Brier Score |
|---|---:|
| Logistic Regression | 0.049421 |
| XGBoost | 0.048588 |

Both models showed reasonable calibration, with XGBoost performing slightly better according to the Brier score.

---

## Risk Ranking

Predicted probabilities were evaluated across ten risk deciles.

The highest-risk decile contained borrowers with substantially higher observed default rates than the lowest-risk decile.

For example:

| Model | Highest-risk decile | Lowest-risk decile |
|---|---:|---:|
| Logistic Regression | 35.97% observed default | 0.30% |
| XGBoost | 37.20% observed default | 0.40% |

This demonstrates strong risk discrimination and meaningful borrower ranking.

---

## Stability Monitoring

Population Stability Index (PSI) was calculated for the model variables and predicted PD distributions.

Reference thresholds:

| PSI | Interpretation |
|---:|---|
| < 0.10 | Stable |
| 0.10–0.25 | Moderate change |
| > 0.25 | Significant change |

### Feature Stability

All 14 monitored variables had PSI values below 0.001.

The highest PSI was:

`income_per_credit_line_clean = 0.000891`

indicating very high stability between the reference and monitoring samples.

### PD Stability

| Model | PSI | Interpretation |
|---|---:|---|
| Logistic Regression | 0.000519 | Stable |
| XGBoost | 0.000215 | Stable |

No material distributional shift was detected.

> **Note:** The reference and monitoring samples in this exercise originate from a random train-test split of the same dataset. Therefore, the PSI analysis demonstrates sample stability rather than true temporal stability. In a production environment, PSI should be calculated using out-of-time or recent portfolio data.

---

## Notebooks

| Notebook | Description |
|---|---|
| `01_eda.ipynb` | Exploratory data analysis |
| `02_data_quality.ipynb` | Data quality assessment |
| `03_feature_engineering.ipynb` | Feature engineering and leakage-safe transformations |
| `04_logistic_pd.ipynb` | Logistic Regression PD model |
| `05_xgboost_challenger.ipynb` | XGBoost challenger model |
| `06_validation.ipynb` | Model validation and calibration |
| `07_monitoring.ipynb` | PSI-based stability monitoring |

---

## Key Conclusions

The PD modeling exercise demonstrates that:

1. Leakage-safe feature engineering substantially improves predictive performance.
2. Logistic Regression provides strong discrimination while maintaining interpretability.
3. XGBoost achieves moderately higher predictive performance.
4. Both models provide meaningful risk ranking across deciles.
5. Both models show reasonable calibration.
6. No significant distributional instability was detected in the validation sample.
7. Logistic Regression is selected as the **champion model**, with XGBoost retained as the **challenger**.

---

## Disclaimer

This project is an educational and portfolio implementation inspired by IFRS 9 credit risk modeling practices.

It is not intended to represent a complete regulatory model implementation.

A production IFRS 9 framework would additionally require elements such as:

- Point-in-time and through-the-cycle considerations
- Macroeconomic scenarios
- Forward-looking information
- Probability-weighted ECL
- Model governance
- Independent validation
- Backtesting
- Override governance
- Monitoring using out-of-time portfolio data