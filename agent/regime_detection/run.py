import json
import sys

from fred_client import fetch_all
from classifier import classify_regime


def main():
    print("Fetching FRED macro data (DGS10, T10Y2Y, FEDFUNDS, VIXCLS)...")
    data = fetch_all(lookback_days=90)
    print("Classifying regime...")
    result = classify_regime(data)

    signals = result['signals']

    print(f"\n  DGS10:  {result['dgs10_current']:.2f}% | yield_spike={signals['yield_spike']}")
    print(f"  T10Y2Y: {result['t10y2y_current']:.2f}%  | curve_inverted={signals['curve_inverted']}")
    vix_str = f"{result['vix_current']:.2f}" if result['vix_current'] else "N/A"
    print(f"  VIX:    {vix_str}     | high_volatility={signals['high_volatility']}")

## 10 year treasury yield wondering if we can compare this historically... maybe we can.. 
## For now we are doing a basic scoring
    if result['dgs10_current'] > 3.8:
        print("This is high by historical standards")

# yield curve this will actually need to pull historic data to compare
    if result['t10y2y_current'] > 0.4:
        print("Curve is flattening")

# FEDFUNDS this will actually need to pull historic data to compare
    if result['fedfunds_current'] > 3.5:
        print("Curve is flattening")

    if result["regime"] == "risk-off":
        print("\n→ RISK-OFF: Recommending USYC allocation")
    else:
        print("\n→ RISK-ON: Opportunity scanner active")

    return result


if __name__ == "__main__":
    main()
