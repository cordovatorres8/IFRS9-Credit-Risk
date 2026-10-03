# IFRS9-Credit-Risk

Portfolio project for credit-risk modelling inspired by IFRS 9, covering:

- **PD (Probability of Default)** — Logistic Regression as an interpretable baseline/champion and XGBoost as challenger.
- **LGD (Loss Given Default)** — regression/beta-regression style workflow depending on the available target.
- **CCF (Credit Conversion Factor)** — experimental portfolio workflow; the dataset must contain sufficient exposure/limit information to construct an observed CCF.
- Validation, calibration, risk bands and monitoring.

> **Important:** This is an educational/portfolio implementation. It is not a complete regulatory IFRS 9 implementation and does not claim regulatory compliance.

## Repository structure

```text
IFRS9-Credit-Risk/
├── PD/
│   ├── data/raw/
│   ├── data/processed/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── README.md
├── LGD/
│   ├── data/raw/
│   ├── data/processed/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── README.md
├── CCF/
│   ├── data/raw/
│   ├── data/processed/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── README.md
├── common/
│   └── metrics.py
├── tests/
├── requirements.txt
└── .gitignore
```

## Workflow

1. Download the public datasets manually and place them under the corresponding `data/raw/` folder.
2. Never commit credentials, API tokens or sensitive banking data.
3. Run the notebooks in numerical order.
4. Save trained models under `models/`.
5. Document assumptions, limitations and validation results.

## Recommended modelling philosophy

### PD
- Target: default within the defined observation horizon.
- Champion: Logistic Regression.
- Challenger: XGBoost.
- Metrics: ROC-AUC, Gini, KS, confusion matrix and calibration.
- Monitoring: PSI and population/risk-band stability.

### LGD
- Define the loss/recovery target carefully.
- Separate defaulted observations from non-defaulted observations when appropriate.
- Evaluate MAE/RMSE and distributional behaviour.
- Document treatment of zero and one boundary values if using a bounded model.

### CCF
CCF should not be fabricated from a dataset that lacks the necessary exposure/limit fields. The project therefore includes a framework that checks for the required columns before modelling.

## Running locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Then open Jupyter:

```bash
jupyter notebook
```
