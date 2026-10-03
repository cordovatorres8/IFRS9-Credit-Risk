import pandas as pd
from sklearn.model_selection import train_test_split

def load_csv(path):
    return pd.read_csv(path)

def clean_basic(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def train_test(df, target, test_size=0.25, random_state=42):
    X = df.drop(columns=[target])
    y = df[target]
    return train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
