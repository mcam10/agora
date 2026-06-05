import matplotlib.pyplot as plt
import scipy.stats as stats

import pandas as pd

from fred_client import fetch_all

DAYS=252

WEIGHTS = {
    "DGS10":    0.25,   # rate stress cluster
    "T10Y2Y":   0.25,   # rate stress cluster — inverse sign
    "FEDFUNDS": 0.15,   # rate stress cluster — least independent
    "VIXCLS":   0.35,   # genuinely independent — deserves more weight
}

def classify_regime(stress_score):

    if stress_score > 2.0: return "CRISIS"
    if stress_score > 0.5: return "RISK_OFF"
    if stress_score > -0.5: return "NEUTRAL"
    return "RISK_ON"

def compute_stress_score(signals, weights):
    """
     Positive score = stress elevated = risk-off
     Sign convention:
      DGS10   high z = stress up   (+)
      T10Y2Y  low z  = stress up   (-) inverted
      FEDFUNDS high z = stress up  (+) but less weight, less independent
      VIXCLS  high z = stress up   (+)
    """

    score = (
        weights["DGS10"]  * signals["DGS10"]["zscore"] +
        weights["T10Y2Y"] * -signals["T10Y2Y"]["zscore"] +
        weights["FEDFUNDS"] * signals["FEDFUNDS"]["zscore"] +
        weights["VIXCLS"] * signals["VIXCLS"]["zscore"] 
 )


    return round(score,4)


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
    stress_score = compute_stress_score(signals, WEIGHTS)
    print(f"\nStress Score: {stress_score:+.4f}")
    print(f"Regime: {classify_regime(stress_score)}")

    # TODO Phase 4: Backtest against 5 years of FRED history

if __name__ == "__main__":
    main()
