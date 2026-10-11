"""Leakage-aware educational LGD estimators."""
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
TARGET = "lgd_time"
POPULATION_FILTER = {"event": 1}
FEATURES = ["LTV"]
LEAKAGE_COLUMNS = ["Recovery_rate", "lgd_time", "y_logistic", "lnrr", "Y_probit", "event"]
def build_baseline():
    return DummyRegressor(strategy="mean")
def build_lgd_model():
    return make_pipeline(SimpleImputer(strategy="median"), LinearRegression())
