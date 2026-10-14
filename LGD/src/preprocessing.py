"""Preprocessing and data preparation for Loss Given Default (LGD) modeling."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

TARGET = "lgd_time"
LEAKAGE_COLUMNS = ["Recovery_rate", "lgd_time", "y_logistic", "lnrr", "Y_probit", "event"]
BASE_FEATURES = ["LTV", "purpose1"]

def load_raw_lgd(data_path: str = "../data/raw/lgd.csv") -> pd.DataFrame:
    """Load raw LGD data and enforce standard types."""
    df = pd.read_csv(data_path)
    return df

def filter_defaulted_population(df: pd.DataFrame) -> pd.DataFrame:
    """Filter population to defaulted contracts (event == 1).
    
    In IFRS 9 / Basel frameworks, LGD is modeled conditional on default.
    """
    filtered = df.loc[df["event"] == 1].copy()
    return filtered

def engineer_lgd_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute non-linear and interaction features from collateral and loan attributes.
    
    - log_LTV: Log-transformed LTV to handle positive skew and extreme ratios.
    - sqrt_LTV: Square root transform for moderate diminishing returns.
    - LTV_sq: Quadratic term to capture accelerated loss when mortgage is heavily underwater.
    - LTV_purpose1: Interaction term between LTV and rental/commercial indicator.
    - LTV_bucket: Categorical regulatory bucket for risk banding (<60%, 60-80%, 80-100%, >100%).
    """
    data = df.copy()
    ltv = np.clip(data["LTV"], 1e-4, None)
    data["log_LTV"] = np.log(ltv)
    data["sqrt_LTV"] = np.sqrt(ltv)
    data["LTV_sq"] = ltv ** 2
    data["LTV_purpose1"] = data["LTV"] * data["purpose1"]
    
    data["LTV_bucket"] = pd.cut(
        data["LTV"],
        bins=[-np.inf, 0.60, 0.80, 1.00, np.inf],
        labels=["LTV_Low_<60", "LTV_Mid_60-80", "LTV_High_80-100", "LTV_Underwater_>100"]
    )
    return data

def prepare_lgd_splits(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42
):
    """Filter to defaulted population, engineer features, and perform stratified split."""
    defaulted = filter_defaulted_population(df)
    featured = engineer_lgd_features(defaulted)
    
    # Feature set safe from leakage
    feature_cols = [
        "LTV", "purpose1", "log_LTV", "sqrt_LTV", "LTV_sq", "LTV_purpose1"
    ]
    
    X = featured[feature_cols]
    y = featured[TARGET]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=featured["purpose1"]
    )
    
    return X_train, X_test, y_train, y_test, featured
