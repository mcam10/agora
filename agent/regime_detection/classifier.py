import pandas as pd

YIELD_SPIKE_THRESHOLD_BPS = 50
LOOKBACK_DAYS = 30


def classify_regime(data: dict[str, pd.DataFrame]) -> dict:
    dgs10 = data["DGS10"]
    t10y2y = data["T10Y2Y"]

    signals = {
        "yield_spike": _detect_yield_spike(dgs10),
        "curve_inverted": _detect_inversion(t10y2y),
    }

    risk_off = any(signals.values())

    return {
        "regime": "risk-off" if risk_off else "risk-on",
        "signals": signals,
        "dgs10_current": float(dgs10["value"].iloc[-1]),
        "t10y2y_current": float(t10y2y["value"].iloc[-1]),
    }


def _detect_yield_spike(dgs10: pd.DataFrame) -> bool:
    if len(dgs10) < LOOKBACK_DAYS:
        return False

    recent = dgs10.tail(LOOKBACK_DAYS)
    change_bps = (recent["value"].iloc[-1] - recent["value"].iloc[0]) * 100
    return change_bps > YIELD_SPIKE_THRESHOLD_BPS


def _detect_inversion(t10y2y: pd.DataFrame) -> bool:
    if t10y2y.empty:
        return False
    return float(t10y2y["value"].iloc[-1]) < 0
