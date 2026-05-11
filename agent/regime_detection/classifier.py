import pandas as pd

YIELD_SPIKE_THRESHOLD_BPS = 50
LOOKBACK_DAYS = 30
VIX_HIGH_THRESHOLD = 25.0


def classify_regime(data: dict[str, pd.DataFrame]) -> dict:
    dgs10 = data["DGS10"]
    t10y2y = data["T10Y2Y"]
    vix = data["VIXCLS"]

    signals = {
        "yield_spike": _detect_yield_spike(dgs10),
        "curve_inverted": _detect_inversion(t10y2y),
        "high_volatility": _detect_high_volatility(vix),
    }

    risk_off = any(signals.values())

    return {
        "regime": "risk-off" if risk_off else "risk-on",
        "signals": signals,
        "dgs10_current": float(dgs10["value"].iloc[-1]),
        "t10y2y_current": float(t10y2y["value"].iloc[-1]),
        "vix_current": float(vix["value"].iloc[-1]) if not vix.empty else None,
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


def _detect_high_volatility(vix: pd.DataFrame) -> bool:
    if vix.empty:
        return False
    return float(vix["value"].iloc[-1]) > VIX_HIGH_THRESHOLD
