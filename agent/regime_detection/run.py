import json
import sys

from fred_client import fetch_all
from classifier import classify_regime
from on_chain import write_regime_on_chain


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

    if result['dgs10_current'] > 3.8:
        print("  ↑ High by historical standards")

    if result['t10y2y_current'] > 0.4:
        print("  ↑ Curve is flattening")

    if result['fedfunds_current'] and result['fedfunds_current'] > 3.5:
        print("  ↑ Fed funds elevated")

    if result["regime"] == "risk-off":
        print("\n→ RISK-OFF: Recommending USYC allocation")
    else:
        print("\n→ RISK-ON: Opportunity scanner active")

    print("\nWriting regime signal on-chain (Arc testnet)...")
    try:
        chain_result = write_regime_on_chain(result)
        if chain_result["registered"]:
            print(f"  ✓ registered | tx: {chain_result['reg_tx']}")
        else:
            print(f"  ✓ {chain_result['reg_tx']}")
        print(f"  ✓ signal written | tx: {chain_result['signal_tx']}")
        print(f"  ✓ agent_code: {chain_result['agent_code']}")
        print(f"  ✓ block: {chain_result['block']} | status: {chain_result['status']}")
    except Exception as e:
        print(f"  ✗ On-chain write failed: {e}")

    return result


if __name__ == "__main__":
    main()
