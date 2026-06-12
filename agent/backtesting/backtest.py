import numpy as np
import os, sys

# Get the path of the outside folder relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
regime_detection = os.path.abspath(os.path.join(script_dir, "..", "regime_detection"))

# Add it to Python's search path
sys.path.insert(0, regime_detection)

from fred_client import fetch_all


#Roughly 5 years
DAYS = 1826

def sharpe_ratio(returns, risk_free_rate=0.001):
    returns = np.array(returns)
    mean = np.mean(returns)
    std = np.std(returns, ddof=1) # ddof=1 divide by n-1
    if std == 0:
        return 0
    return (mean - risk_free_rate) / std

five_year_data = fetch_all(lookback_days=DAYS)
print(five_year_data)

