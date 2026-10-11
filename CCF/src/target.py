"""Target construction and schema checks for revolving-credit CCF/LEQ."""
from collections.abc import Iterable
import numpy as np
import pandas as pd

LEQ_COLUMNS = ("ead_at_default", "balance_at_observation", "limit_at_observation")
CCF_COLUMNS = ("ead_at_default", "balance_at_observation")

def audit_ccf_schema(columns: Iterable[str]) -> pd.DataFrame:
    available = set(columns)
    return pd.DataFrame([
        {"field": field, "available": field in available, "meaning": meaning}
        for field, meaning in [
            ("ead_at_default", "EAD/saldo utilizado en la fecha de default"),
            ("balance_at_observation", "Saldo en fecha pre-default de observación"),
            ("limit_at_observation", "Límite comprometido en la misma observación"),
        ]
    ])

def calculate_leq(ead_at_default, balance_at_observation, limit_at_observation, denominator_floor: float = 0.0) -> pd.Series:
    """LEQ = (EAD_T - B_t)/(L_t - B_t); undefined small denominators become NaN.

    No winsorization/clipping is applied; inspect negative/>1 values as data/model outcomes.
    """
    ead, balance, limit_ = np.broadcast_arrays(ead_at_default, balance_at_observation, limit_at_observation)
    denom = limit_ - balance
    valid = np.isfinite(ead) & np.isfinite(balance) & np.isfinite(limit_) & (denom > denominator_floor)
    result = np.full(denom.shape, np.nan, dtype=float)
    result[valid] = (ead[valid] - balance[valid]) / denom[valid]
    return pd.Series(result.ravel())

def calculate_ccf(ead_at_default, balance_at_observation, denominator_floor: float = 0.0) -> pd.Series:
    """Alternative convention CCF = EAD_T/B_t; small balance denominators -> NaN."""
    ead, balance = np.broadcast_arrays(ead_at_default, balance_at_observation)
    valid = np.isfinite(ead) & np.isfinite(balance) & (np.abs(balance) > denominator_floor)
    result = np.full(balance.shape, np.nan, dtype=float)
    result[valid] = ead[valid] / balance[valid]
    return pd.Series(result.ravel())
