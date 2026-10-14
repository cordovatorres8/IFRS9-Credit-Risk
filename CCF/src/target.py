"""Target construction, schema checks, and EAD calculation for revolving-credit CCF/LEQ."""
from collections.abc import Iterable
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

LEQ_COLUMNS = ("ead_at_default", "balance_at_observation", "limit_at_observation")
CCF_COLUMNS = ("ead_at_default", "balance_at_observation")


def audit_ccf_schema(columns: Iterable[str]) -> pd.DataFrame:
    """Audit column presence against required IFRS 9 revolving credit fields."""
    available = set(columns)
    return pd.DataFrame([
        {"field": field, "available": field in available, "meaning": meaning}
        for field, meaning in [
            ("ead_at_default", "EAD/saldo utilizado en la fecha de default (T)"),
            ("balance_at_observation", "Saldo utilizado en la fecha de observación (t)"),
            ("limit_at_observation", "Límite comprometido en la fecha de observación (t)"),
        ]
    ])


def calculate_leq(
    ead_at_default,
    balance_at_observation,
    limit_at_observation,
    denominator_floor: float = 50.0
) -> pd.Series:
    """Calculate Loan Equivalent Exposure (LEQ).
    
    LEQ = (EAD_T - Balance_t) / (Limit_t - Balance_t)
    When undrawn limit (Limit_t - Balance_t) is zero or negligible (< denominator_floor),
    LEQ is undefined (NaN) to prevent numerical instability.
    """
    ead = np.asarray(ead_at_default, dtype=float)
    balance = np.asarray(balance_at_observation, dtype=float)
    limit_ = np.asarray(limit_at_observation, dtype=float)
    
    undrawn = limit_ - balance
    valid = np.isfinite(ead) & np.isfinite(balance) & np.isfinite(limit_) & (undrawn > denominator_floor)
    
    result = np.full(undrawn.shape, np.nan, dtype=float)
    result[valid] = (ead[valid] - balance[valid]) / undrawn[valid]
    return pd.Series(result)


def calculate_ccf(
    ead_at_default,
    balance_at_observation,
    denominator_floor: float = 50.0
) -> pd.Series:
    """Calculate alternative Basel CCF convention: CCF = EAD_T / Balance_t."""
    ead = np.asarray(ead_at_default, dtype=float)
    balance = np.asarray(balance_at_observation, dtype=float)
    
    valid = np.isfinite(ead) & np.isfinite(balance) & (balance > denominator_floor)
    result = np.full(balance.shape, np.nan, dtype=float)
    result[valid] = ead[valid] / balance[valid]
    return pd.Series(result)


def reconstruct_ead_from_leq(
    balance_at_obs,
    limit_at_obs,
    predicted_leq
) -> pd.Series:
    """Reconstruct monetary Exposure at Default (EAD) from predicted LEQ.
    
    EAD = Balance_t + LEQ_pred * (Limit_t - Balance_t)
    Ensures EAD >= Balance_t.
    """
    balance = np.asarray(balance_at_obs, dtype=float)
    limit_ = np.asarray(limit_at_obs, dtype=float)
    leq = np.asarray(predicted_leq, dtype=float)
    
    undrawn = np.maximum(limit_ - balance, 0.0)
    ead = balance + leq * undrawn
    return pd.Series(ead)
