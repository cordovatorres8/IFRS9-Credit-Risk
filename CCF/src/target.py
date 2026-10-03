import pandas as pd

def calculate_ccf(df, ead_col, drawn_col, undrawn_col):
    required = [ead_col, drawn_col, undrawn_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns required to construct CCF: {missing}"
        )

    out = df.copy()
    denom = out[undrawn_col]
    out["CCF"] = (out[ead_col] - out[drawn_col]) / denom.replace(0, pd.NA)
    return out
