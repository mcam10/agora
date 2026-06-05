import matplotlib.pyplot as plt
import scipy.stats as stats

from fred_client import fetch_all

DAYS=252



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
    print(f"Percentile {percentile} {percentile:.2f}%")
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

    # TODO Phase 3: Re-enable classifier with weighted composite score

if __name__ == "__main__":
    main()
