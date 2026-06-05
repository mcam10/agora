import matplotlib.pyplot as plt
import scipy.stats as stats

import pandas as pd

from fred_client import fetch_all

DAYS=252



def compute_correlations(data, signals):
    combined = pd.DataFrame({
        key: data[key].set_index("date")["value"]
        for key in signals
        if data.get(key) is not None
        }).dropna()

    corr = combined.corr()
    print("\nSignal Correlation Matrix:")
    print(corr.round(2).to_string())
    return corr

def compute_signal(data, key, label):
    df = data.get(key)
    if df is None:
        print(f"No {label} data found")
        return {}

    vals = df['value']
    current = vals.iloc[-1]
    mean = vals.mean()
    std = vals.std()
    percentile = stats.percentileofscore(vals, current)
    zscore = (current - mean) / std

    print(f"Current {label} value: {current:.2f}")
    print(f"Percentile {percentile:.2f}%")
    print(f"Z-Score {zscore:+.4f}\n")

    return {
        "current": round(current, 4),
        "percentile": round(percentile, 2),
        "zscore": round(zscore, 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
    }


def main():
    print("Fetching FRED macro data (DGS10, T10Y2Y, FEDFUNDS, VIXCLS)...")
    data = fetch_all(lookback_days=DAYS)

    signals = {
        "DGS10": compute_signal(data, "DGS10", "DGS10 (10Y Yield)"),
        "T10Y2Y": compute_signal(data, "T10Y2Y", "T10Y2Y (Yield Curve)"),
        "FEDFUNDS": compute_signal(data, "FEDFUNDS", "Fed Funds Rate"),
        "VIXCLS": compute_signal(data, "VIXCLS", "VIX"),
   }
    corr = compute_correlations(data, signals) 

    # TODO Phase 3: Re-enable classifier with weighted composite score

if __name__ == "__main__":
    main()
