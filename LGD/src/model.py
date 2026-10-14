"""LGD Model implementations: Baseline, Linear Regression, Fractional Logit, Two-Stage Hurdle, and XGBoost."""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import statsmodels.api as sm
import statsmodels.formula.api as smf
import xgboost as xgb


class FractionalLogitLGD(BaseEstimator, RegressorMixin):
    """Fractional Logit Generalized Linear Model (GLM) for bounded continuous outcomes [0, 1].
    
    In credit risk, LGD represents a proportion bounded between 0 and 1. Standard OLS can
    predict negative values or values exceeding 100%. Fractional Logit (Papke & Wooldridge, 1996)
    uses a Quasi-Binomial family with a Logit link, strictly enforcing predicted LGD in (0, 1).
    """
    def __init__(self, add_constant: bool = True):
        self.add_constant = add_constant
        self.model_ = None
        self.results_ = None
        self.feature_names_ = None

    def fit(self, X, y):
        X_df = pd.DataFrame(X)
        self.feature_names_ = list(X_df.columns)
        
        # Clip y slightly away from exact 0 and 1 for numerical stability if needed
        y_clipped = np.clip(np.asarray(y), 1e-5, 1 - 1e-5)
        
        if self.add_constant:
            X_design = sm.add_constant(X_df, has_constant='add')
        else:
            X_design = X_df

        glm_binom = sm.GLM(
            y_clipped,
            X_design,
            family=sm.families.Binomial(link=sm.families.links.Logit())
        )
        self.results_ = glm_binom.fit(disp=False)
        return self

    def predict(self, X):
        X_df = pd.DataFrame(X)
        if self.add_constant:
            X_design = sm.add_constant(X_df, has_constant='add')
        else:
            X_design = X_df
        pred = self.results_.predict(X_design)
        return np.asarray(pred)


class TwoStageLGD(BaseEstimator, RegressorMixin):
    """Two-Stage Hurdle Model for LGD with mass point at zero loss.
    
    Stage 1: Logistic Regression predicting the probability of experiencing a loss (LGD > threshold).
    Stage 2: Regression estimating loss severity conditional on experiencing a loss (LGD | LGD > threshold).
    Expected LGD = P(Loss > 0) * E[Loss | Loss > 0].
    """
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
        self.clf_ = LogisticRegression(max_iter=1000)
        self.reg_ = LinearRegression()

    def fit(self, X, y):
        X_arr = np.asarray(X)
        y_arr = np.asarray(y)
        
        # Stage 1: Binary indicator of material loss
        has_loss = (y_arr > self.threshold).astype(int)
        self.clf_.fit(X_arr, has_loss)
        
        # Stage 2: Fit on positive loss cases
        if has_loss.sum() > 0:
            self.reg_.fit(X_arr[has_loss == 1], y_arr[has_loss == 1])
        else:
            self.reg_.fit(X_arr, y_arr)
        return self

    def predict(self, X):
        X_arr = np.asarray(X)
        p_loss = self.clf_.predict_proba(X_arr)[:, 1]
        severity = self.reg_.predict(X_arr)
        # Severity bounded within [0, 1]
        severity_bounded = np.clip(severity, 0.0, 1.0)
        return p_loss * severity_bounded


def build_baseline_mean():
    """Baseline predicting training sample mean."""
    return DummyRegressor(strategy="mean")

def build_linear_lgd():
    """Interpretable OLS regression benchmark."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("ols", LinearRegression())
    ])

def build_fractional_logit_lgd():
    """Champion econometric model: Fractional Logit GLM."""
    return FractionalLogitLGD(add_constant=True)

def build_two_stage_lgd(threshold: float = 0.05):
    """Two-Stage hurdle model separating zero/near-zero loss cures from losses."""
    return TwoStageLGD(threshold=threshold)

def build_xgboost_lgd():
    """Challenger machine learning model: Gradient Boosted Trees."""
    return xgb.XGBRegressor(
        n_estimators=120,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        objective="reg:squarederror"
    )
