# Opportunity scanner — strategy logic is private.
# This module exposes only the interface used by the regime detection layer.


def scan_opportunities(regime: dict) -> list[dict]:
    """
    Scans available strategies and returns ranked opportunities.
    Only activates during risk-on regimes.
    """
    if regime["regime"] == "risk-off":
        return []

    # Private strategy logic not included in open-source release
    raise NotImplementedError("Strategy scanner is private — see README")
