import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

def gini_from_auc(auc: float) -> float:
    return 2 * auc - 1

def ks_statistic(y_true, y_score) -> float:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    order = np.argsort(-y_score)
    y = y_true[order]
    bad = np.cumsum(y) / max(y.sum(), 1)
    good = np.cumsum(1 - y) / max((1 - y).sum(), 1)
    return float(np.max(np.abs(bad - good)))

def binary_metrics(y_true, y_score, threshold=0.5):
    auc = roc_auc_score(y_true, y_score)
    pred = (np.asarray(y_score) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "auc": float(auc),
        "gini": float(gini_from_auc(auc)),
        "ks": ks_statistic(y_true, y_score),
        "threshold": threshold,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

def regression_metrics(y_true, y_pred):
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }
