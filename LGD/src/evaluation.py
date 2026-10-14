"""Evaluation and validation metrics for LGD models."""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, median_absolute_error

def evaluate_lgd_model(y_true, y_pred, model_name: str = "Model") -> Dict[str, Any]:
    """Calculate comprehensive credit risk regression metrics for LGD."""
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    
    mae = mean_absolute_error(y_true_arr, y_pred_arr)
    rmse = root_mean_squared_error(y_true_arr, y_pred_arr)
    r2 = r2_score(y_true_arr, y_pred_arr)
    medae = median_absolute_error(y_true_arr, y_pred_arr)
    
    # Check bounded consistency: LGD must be in [0, 1]
    out_of_bounds = int(((y_pred_arr < 0.0) | (y_pred_arr > 1.0)).sum())
    out_of_bounds_pct = (out_of_bounds / len(y_pred_arr)) * 100.0
    
    # Portfolio-level aggregate loss bias
    mean_actual = float(np.mean(y_true_arr))
    mean_pred = float(np.mean(y_pred_arr))
    bias = mean_pred - mean_actual
    
    return {
        "model": model_name,
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "medae": float(medae),
        "mean_actual": mean_actual,
        "mean_pred": mean_pred,
        "bias": float(bias),
        "out_of_bounds_count": out_of_bounds,
        "out_of_bounds_pct": float(out_of_bounds_pct)
    }

def compute_decile_calibration(y_true, y_pred, feature_values, n_bins: int = 10) -> pd.DataFrame:
    """Evaluate calibration and risk discrimination across feature deciles."""
    df = pd.DataFrame({
        "feature": np.asarray(feature_values),
        "actual": np.asarray(y_true),
        "predicted": np.asarray(y_pred)
    })
    df["decile"] = pd.qcut(df["feature"], q=n_bins, duplicates="drop")
    
    grouped = df.groupby("decile", observed=True).agg(
        count=("actual", "count"),
        feature_min=("feature", "min"),
        feature_max=("feature", "max"),
        mean_actual=("actual", "mean"),
        mean_predicted=("predicted", "mean")
    ).reset_index()
    
    grouped["abs_diff"] = (grouped["mean_actual"] - grouped["mean_predicted"]).abs()
    grouped["ratio_pred_actual"] = grouped["mean_predicted"] / grouped["mean_actual"].replace(0, np.nan)
    return grouped

def calculate_continuous_psi(reference: np.ndarray, current: np.ndarray, n_bins: int = 10) -> Tuple[float, pd.DataFrame]:
    """Calculate Population Stability Index (PSI) for continuous distributions (e.g. LTV or predicted LGD)."""
    ref = np.asarray(reference)
    cur = np.asarray(current)
    
    # Define bin edges on reference sample
    percentiles = np.linspace(0, 100, n_bins + 1)
    bin_edges = np.percentile(ref, percentiles)
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf
    bin_edges = np.unique(bin_edges)
    
    ref_counts, _ = np.histogram(ref, bins=bin_edges)
    cur_counts, _ = np.histogram(cur, bins=bin_edges)
    
    ref_pct = np.clip(ref_counts / len(ref), 1e-4, 1.0)
    cur_pct = np.clip(cur_counts / len(cur), 1e-4, 1.0)
    
    psi_vec = (cur_pct - ref_pct) * np.log(cur_pct / ref_pct)
    total_psi = float(np.sum(psi_vec))
    
    table = pd.DataFrame({
        "bin": range(1, len(ref_pct) + 1),
        "ref_share": ref_pct,
        "cur_share": cur_pct,
        "psi_contribution": psi_vec
    })
    
    return total_psi, table
