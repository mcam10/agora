import matplotlib.pyplot as plt
import scipy.stats as stats

from fred_client import fetch_all


def main():
    print("Fetching FRED macro data (DGS10, T10Y2Y, FEDFUNDS, VIXCLS)...")
    data = fetch_all(lookback_days=90)

    # --- DGS10: Percentile scoring (88th pct as of 2026-05-29) ---
    dgs_10_data = data.get("DGS10", "No DGS10 data found")
    current_value = dgs_10_data['value'].iloc[-1]
    percentile = stats.percentileofscore(dgs_10_data['value'], current_value)
    print(f"Current DGS10 value: {current_value:.2f}")
    print(f"Percentile of current DGS10 value: {percentile:.2f}%")

    # --- T10Y2Y: Yield curve spread (5th-6th pct = flattening) ---
    t102y_data = data.get("T10Y2Y", "No T10Y2Y Found")
    plt.hist(t102y_data['value'], bins=30, alpha=0.7, label='T10Y2Y Distribution')
    plt.axvline(t102y_data['value'].iloc[-1], color='red', linestyle='--', label='Current Value')
    plt.xlabel('T10Y2Y Value')
    plt.ylabel('Frequency')
    plt.title('Distribution of T10Y2Y Values (Past 90 days)')
    plt.legend()
    plt.show()
    t102y_current_value = t102y_data['value'].iloc[-1]
    t102y_percentile = stats.percentileofscore(t102y_data['value'], t102y_current_value)
    print(f"Current T10Y2Y value: {t102y_current_value:.2f}")
    print(f"Percentile of current T10Y2Y value: {t102y_percentile:.2f}%")

    # TODO Phase 2: Add FEDFUNDS + VIXCLS percentile scoring
    # TODO Phase 2: Replace 90-day lookback with 252+ days
    # TODO Phase 2: Add z-score normalization via summarize_signals()
    # TODO Phase 3: Re-enable classifier with weighted composite score

if __name__ == "__main__":
    main()
