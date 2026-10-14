"""Financial exposure and statistical metrics for Credit Conversion Factor (CCF/LEQ) and EAD."""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score


def evaluate_ccf_model(
    y_true_leq,
    y_pred_leq,
    balance_obs,
    limit_obs,
    ead_true,
    model_name: str = "CCF Model"
) -> Dict[str, Any]:
    """Calculate both statistical LEQ accuracy and financial EAD exposure accuracy."""
    y_true = np.asarray(y_true_leq, dtype=float)
    y_pred = np.asarray(y_pred_leq, dtype=float)
    b_obs = np.asarray(balance_obs, dtype=float)
    l_obs = np.asarray(limit_obs, dtype=float)
    ead_actual = np.asarray(ead_true, dtype=float)
    
    # 1. Statistical LEQ Metrics
    mae_leq = mean_absolute_error(y_true, y_pred)
    rmse_leq = root_mean_squared_error(y_true, y_pred)
    r2_leq = r2_score(y_true, y_pred)
    
    # 2. Financial EAD Reconstruction
    undrawn = np.maximum(l_obs - b_obs, 0.0)
    ead_pred = b_obs + y_pred * undrawn
    
    total_ead_actual = float(np.sum(ead_actual))
    total_ead_pred = float(np.sum(ead_pred))
    dollar_bias = total_ead_pred - total_ead_actual
    pct_bias = (dollar_bias / total_ead_actual) * 100.0
    ead_mae = float(mean_absolute_error(ead_actual, ead_pred))
    ead_rmse = float(root_mean_squared_error(ead_actual, ead_pred))
    
    return {
        "model": model_name,
        "mae_leq": float(mae_leq),
        "rmse_leq": float(rmse_leq),
        "r2_leq": float(r2_leq),
        "total_ead_actual": total_ead_actual,
        "total_ead_pred": total_ead_pred,
        "dollar_bias": float(dollar_bias),
        "pct_bias": float(pct_bias),
        "ead_dollar_mae": ead_mae,
        "ead_dollar_rmse": ead_rmse
    }


def compute_ecl_impact(
    pd_estimates: np.ndarray,
    lgd_estimates: np.ndarray,
    balance_obs: np.ndarray,
    limit_obs: np.ndarray,
    ccf_regulatory: np.ndarray,
    ccf_model: np.ndarray
) -> pd.DataFrame:
    """Compute portfolio-level IFRS 9 ECL under Regulatory CCF vs Model-based CCF.
    
    ECL = PD * LGD * EAD
    where EAD = Balance + CCF * (Limit - Balance)
    """
    pd_val = np.asarray(pd_estimates)
    lgd_val = np.asarray(lgd_estimates)
    b = np.asarray(balance_obs)
    l = np.asarray(limit_obs)
    undrawn = np.maximum(l - b, 0.0)
    
    ead_reg = b + np.asarray(ccf_regulatory) * undrawn
    ead_mod = b + np.asarray(ccf_model) * undrawn
    
    ecl_reg = pd_val * lgd_val * ead_reg
    ecl_mod = pd_val * lgd_val * ead_mod
    
    return pd.DataFrame({
        "Total_Exposure_Regulatory": [float(np.sum(ead_reg))],
        "Total_Exposure_Model": [float(np.sum(ead_mod))],
        "Exposure_Difference": [float(np.sum(ead_mod) - np.sum(ead_reg))],
        "Total_ECL_Regulatory": [float(np.sum(ecl_reg))],
        "Total_ECL_Model": [float(np.sum(ecl_mod))],
        "ECL_Difference": [float(np.sum(ecl_mod) - np.sum(ecl_reg))],
        "ECL_Capital_Relief_Pct": [float((np.sum(ecl_reg) - np.sum(ecl_mod)) / np.sum(ecl_reg) * 100.0)]
    })
