import json
import sys

from .fred_client import fetch_all
from .classifier import classify_regime


def main():
    print("Fetching FRED macro data...")
    data = fetch_all(lookback_days=90)

    print("Classifying regime...")
    result = classify_regime(data)

    print(json.dumps(result, indent=2))

    if result["regime"] == "risk-off":
        print("\n→ RISK-OFF: Recommending USYC allocation")
    else:
        print("\n→ RISK-ON: Opportunity scanner active")

    return result


if __name__ == "__main__":
    main()
