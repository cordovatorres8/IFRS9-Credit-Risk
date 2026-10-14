"""CCF / LEQ Model implementations: Regulatory Benchmark, Historical Mean, Segmented Grid, Fractional Logit, and XGBoost."""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import statsmodels.api as sm
import xgboost as xgb


class RegulatoryBenchmarkCCF(BaseEstimator, RegressorMixin):
    """Basel Standardized / Regulatory Fixed CCF benchmark.
    
    Assigns regulatory conversion factors by product type:
    - Credit Card: 75%
    - Overdraft: 50%
    - Revolving Line: 75%
    """
    def __init__(self, factors: Dict[str, float] = None):
        self.factors = factors or {
            "Credit Card": 0.75,
            "Overdraft": 0.50,
            "Revolving Line": 0.75
        }

    def fit(self, X, y=None):
        return self

    def predict(self, X):
        X_df = pd.DataFrame(X)
        if "product_type" in X_df.columns:
            preds = X_df["product_type"].map(self.factors).fillna(0.75).values
        else:
            preds = np.full(len(X_df), 0.75)
        return preds


class SegmentedGridCCF(BaseEstimator, RegressorMixin):
    """Segmented CCF Lookup Table based on Pre-Default Utilization Deciles and Product Type.
    
    Standard bank internal rating practice: lookup matrix of historical average LEQ.
    """
    def __init__(self, n_bins: int = 5):
        self.n_bins = n_bins
        self.lookup_ = {}
        self.global_mean_ = 0.75

    def fit(self, X, y):
        df = pd.DataFrame(X).copy()
        df["target"] = np.asarray(y)
        self.global_mean_ = float(df["target"].mean())
        
        # Segment by product and utilization bin
        df["util_bin"] = pd.qcut(df["utilization_obs"], q=self.n_bins, duplicates="drop")
        grouped = df.groupby(["product_type", "util_bin"], observed=True)["target"].mean()
        self.lookup_ = grouped.to_dict()
        return self

    def predict(self, X):
        df = pd.DataFrame(X).copy()
        df["util_bin"] = pd.qcut(df["utilization_obs"], q=self.n_bins, duplicates="drop")
        preds = []
        for _, row in df.iterrows():
            key = (row["product_type"], row["util_bin"])
            val = self.lookup_.get(key, self.global_mean_)
            preds.append(val)
        return np.asarray(preds)


class FractionalLogitCCF(BaseEstimator, RegressorMixin):
    """Fractional Logit GLM for Bounded Conversion Factors [0, 1].
    
    Guarantees predicted LEQ strictly stays between 0% and 100%.
    """
    def __init__(self, add_constant: bool = True):
        self.add_constant = add_constant
        self.results_ = None
        self.feature_names_ = None

    def fit(self, X, y):
        X_df = pd.DataFrame(X)
        self.feature_names_ = list(X_df.columns)
        
        y_clipped = np.clip(np.asarray(y), 1e-4, 1.0 - 1e-4)
        
        if self.add_constant:
            X_design = sm.add_constant(X_df, has_constant='add')
        else:
            X_design = X_df
            
        glm = sm.GLM(
            y_clipped,
            X_design,
            family=sm.families.Binomial(link=sm.families.links.Logit())
        )
        self.results_ = glm.fit(disp=False)
        return self

    def predict(self, X):
        X_df = pd.DataFrame(X)
        if self.add_constant:
            X_design = sm.add_constant(X_df, has_constant='add')
        else:
            X_design = X_df
        return np.asarray(self.results_.predict(X_design))


def build_regulatory_ccf():
    return RegulatoryBenchmarkCCF()

def build_segmented_ccf():
    return SegmentedGridCCF(n_bins=5)

def build_fractional_logit_ccf():
    return FractionalLogitCCF(add_constant=True)

def build_xgboost_ccf():
    return xgb.XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        objective="reg:squarederror"
    )
