import numpy as np

def sharpe_ratio(returns, risk_free_rate=0.001):
    returns = np.array(returns)
    mean = np.mean(returns)
    std = np.std(returns, ddof=1) # ddof=1 divide by n-1
    if std == 0:
        return 0
    return (mean - risk_free_rate) / std


