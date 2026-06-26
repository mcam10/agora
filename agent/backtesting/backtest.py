import numpy as np
import pandas as pd
import os, sys, json
import scipy.stats as stats

script_dir = os.path.dirname(os.path.abspath(__file__))
regime_detection = os.path.abspath(os.path.join(script_dir, "..", "regime_detection"))
sys.path.insert(0, regime_detection)

from fred_client import fetch_all
from run import compute_stress_score, classify_regime, WEIGHTS

LOOKBACK_DAYS = 252
OBSERVATION_START_DAYS = 1826


def sharpe_ratio(returns, risk_free_rate=0.001):
    returns = np.array(returns)
    mean = np.mean(returns)
    std = np.std(returns, ddof=1)
    if std == 0:
        return 0
    return (mean - risk_free_rate) / std


def compute_window_signal(vals):
    """Compute z-score and percentile for a single series window."""
    current = vals.iloc[-1]
    mean = vals.mean()
    std = vals.std()
    if std == 0:
        return {"current": current, "percentile": 50.0, "zscore": 0.0, "mean": mean, "std": 0.0}

    percentile = stats.percentileofscore(vals, current)
    zscore = (current - mean) / std

    return {
        "current": round(current, 4),
        "percentile": round(percentile, 2),
        "zscore": round(zscore, 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
    }


def run_backtest(window=252):
    """
    Slide a 252-day window across 5 years of FRED data.
    At each step, compute stress score and classify regime.
    Returns a DataFrame: date | stress_score | regime
    """
    print("Fetching 5 years of FRED history...")
    full_history = fetch_all(observation_start=0, lookback_days=OBSERVATION_START_DAYS)

    all_dates = full_history["DGS10"]["date"].values
    results = []

    print(f"Running backtest: {len(all_dates) - window} windows...")

    for i in range(window, len(all_dates)):
        window_start = all_dates[i - window]
        window_end = all_dates[i]

        signals = {}
        skip = False
        for key, df in full_history.items():
            slice_df = df[(df["date"] >= window_start) & (df["date"] <= window_end)]
            if len(slice_df) < 10:
                skip = True
                break
            signals[key] = compute_window_signal(slice_df["value"])

        if skip:
            continue

        stress = compute_stress_score(signals, WEIGHTS)
        regime = classify_regime(stress)

        results.append({
            "date": pd.Timestamp(window_end),
            "stress_score": stress,
            "regime": regime,
        })

    df = pd.DataFrame(results)
    print(f"\nBacktest complete: {len(df)} data points")
    print(f"Date range: {df['date'].iloc[0].date()} → {df['date'].iloc[-1].date()}")
    print(f"\nRegime distribution:")
    print(df["regime"].value_counts().to_string())
    print(f"\nStress score stats:")
    print(f"  Mean:  {df['stress_score'].mean():+.4f}")
    print(f"  Std:   {df['stress_score'].std():.4f}")
    print(f"  Min:   {df['stress_score'].min():+.4f}")
    print(f"  Max:   {df['stress_score'].max():+.4f}")

    return df


if __name__ == "__main__":
    results = run_backtest()
    results.to_csv(os.path.join(script_dir, "backtest_results.csv"), index=False)
    print("\nResults saved to backtest_results.csv")

