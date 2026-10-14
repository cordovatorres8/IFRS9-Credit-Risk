"""Revolving credit portfolio generator for IFRS 9 / Basel EAD & CCF modeling.

Generates realistic pre-default and default-time behavioral snapshots for revolving facilities
(credit cards, personal overdrafts, and revolving lines of credit) with proper time alignment.
"""
from pathlib import Path
import numpy as np
import pandas as pd


def generate_revolving_portfolio(
    n_accounts: int = 15000,
    default_rate: float = 0.085,
    random_state: int = 42
) -> pd.DataFrame:
    """Generate a realistic revolving credit portfolio dataset.
    
    Includes 12-month pre-default observation (t) and default-date realization (T).
    """
    rng = np.random.default_rng(random_state)
    
    # 1. Facility & Borrower Attributes
    account_ids = [f"ACC_{i+100001:06d}" for i in range(n_accounts)]
    products = rng.choice(
        ["Credit Card", "Overdraft", "Revolving Line"],
        size=n_accounts,
        p=[0.60, 0.25, 0.15]
    )
    
    # Credit Limit: log-normal distribution rounded to $500
    base_limit = np.exp(rng.normal(loc=8.8, scale=0.6, size=n_accounts))
    credit_limit = np.round(np.clip(base_limit, 1000, 60000) / 500) * 500
    
    # Borrower characteristics at observation date (t)
    credit_score = np.clip(np.round(rng.normal(650, 65, size=n_accounts)), 320, 850).astype(int)
    months_on_book = rng.integers(6, 120, size=n_accounts)
    annual_income = np.round(np.clip(np.exp(rng.normal(10.5, 0.45, size=n_accounts)), 18000, 250000), -2)
    
    # Delinquency status at observation date (t)
    delinq_rand = rng.random(size=n_accounts)
    is_low_score = credit_score < 600
    delinquency_bucket = []
    for r, low in zip(delinq_rand, is_low_score):
        if low:
            if r < 0.55:
                delinquency_bucket.append("0 DPD")
            elif r < 0.85:
                delinquency_bucket.append("1-29 DPD")
            else:
                delinquency_bucket.append("30-59 DPD")
        else:
            if r < 0.88:
                delinquency_bucket.append("0 DPD")
            elif r < 0.97:
                delinquency_bucket.append("1-29 DPD")
            else:
                delinquency_bucket.append("30-59 DPD")
    delinquency_bucket = np.array(delinquency_bucket)
    
    # 2. Pre-default balance & utilization at observation date (t)
    score_factor = (850 - credit_score) / 530.0
    util_shape1 = 1.2 + 2.5 * score_factor
    util_shape2 = 3.5 - 1.5 * score_factor
    utilization_obs = np.clip(rng.beta(util_shape1, np.maximum(util_shape2, 0.8), size=n_accounts), 0.02, 0.98)
    
    balance_obs = np.round(credit_limit * utilization_obs, 2)
    undrawn_obs = credit_limit - balance_obs
    
    payment_ratio = np.clip(rng.beta(2.0, 5.0, size=n_accounts) * (credit_score / 700.0), 0.01, 1.0)
    
    # 3. 12-month Default Flag
    score_term = -0.012 * (credit_score - 650)
    util_term = 2.2 * (utilization_obs - 0.5)
    delinq_term = np.where(delinquency_bucket == "30-59 DPD", 1.8, 
                  np.where(delinquency_bucket == "1-29 DPD", 0.9, 0.0))
    
    logit_p = -3.1 + score_term + util_term + delinq_term
    prob_default = 1.0 / (1.0 + np.exp(-logit_p))
    prob_default = prob_default * (default_rate / prob_default.mean())
    prob_default = np.clip(prob_default, 0.001, 0.95)
    default_flag = (rng.random(size=n_accounts) < prob_default).astype(int)
    
    # 4. Exposure at Default (EAD) & LEQ Realization at (T)
    base_drawdown_rate = rng.beta(2.5, 1.5, size=n_accounts) # mean ~0.625
    adj_drawdown_rate = np.clip(base_drawdown_rate + 0.15 * utilization_obs + 0.10 * (credit_score < 580), 0.05, 0.98)
    
    additional_drawdown = undrawn_obs * adj_drawdown_rate
    interest_and_fees = balance_obs * rng.uniform(0.02, 0.06, size=n_accounts)
    
    ead_default = np.where(
        default_flag == 1,
        np.round(balance_obs + additional_drawdown + interest_and_fees, 2),
        np.nan
    )
    
    realized_leq = np.where(
        (default_flag == 1) & (undrawn_obs > 50),
        np.clip((ead_default - balance_obs) / undrawn_obs, 0.0, 1.5),
        np.nan
    )
    
    realized_ccf = np.where(
        (default_flag == 1) & (balance_obs > 50),
        ead_default / balance_obs,
        np.nan
    )
    
    df = pd.DataFrame({
        "account_id": account_ids,
        "product_type": products,
        "credit_limit": credit_limit,
        "balance_obs": balance_obs,
        "utilization_obs": np.round(utilization_obs, 4),
        "undrawn_obs": np.round(undrawn_obs, 2),
        "delinquency_bucket": delinquency_bucket,
        "credit_score": credit_score,
        "months_on_book": months_on_book,
        "annual_income": annual_income,
        "payment_ratio": np.round(payment_ratio, 4),
        "default_flag": default_flag,
        "ead_at_default": ead_default,
        "realized_leq": np.round(realized_leq, 4),
        "realized_ccf": np.round(realized_ccf, 4)
    })
    
    return df


if __name__ == "__main__":
    out_dir = Path("CCF/data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "revolving_ccf_portfolio.csv"
    df = generate_revolving_portfolio()
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df):,} accounts to {out_path}.")
    defaulted = df.query("default_flag == 1")
    print(f"Defaulted accounts: {len(defaulted):,} ({len(defaulted)/len(df):.1%})")
    print(f"Mean Realized LEQ: {defaulted['realized_leq'].mean():.3f}")
    print(f"Mean Realized CCF: {defaulted['realized_ccf'].mean():.3f}")
