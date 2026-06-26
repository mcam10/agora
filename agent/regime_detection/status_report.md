# Macro Regime Detector — Progression Log

A running record of analytical decisions, findings, and next steps as this project evolves from a static scoring system into a mathematically grounded regime detection engine.

---

## Phase 1 — Percentile-Based Signal Scoring (Complete)

### What We Built
Replaced hardcoded thresholds (e.g. `vix < 15 → score 2`) with rolling percentile scoring using `scipy.stats.percentileofscore`. Each signal is now ranked within its own historical distribution, making the detector self-calibrating as macro conditions shift.

### Key Findings

**DGS10 (10-Year Treasury Yield)**
- Current value: ~4.46–4.47%
- Percentile (90-day window): **88th percentile**
- Interpretation: The current yield exceeds 88% of observations in the recent window. Elevated by recent historical standards. Consistent with the broader macro picture — higher borrowing costs, headwind for growth equities, TLT suppressed.
- Note: As of late April 2026, the 10Y sits at ~4.40–4.47%, representing a fundamentally different rate environment than the 2010s when yields hovered near record lows.

**T10Y2Y (10Y–2Y Yield Curve Spread)**
- Current value: ~0.47–0.50%
- Percentile (90-day window): **5th–6th percentile**
- Interpretation: The curve is near its flattest point of the recent window. A low T10Y2Y value signals investor concern about growth and potential recession. Started the 90-day window at +0.65%, compressed to +0.47% — flattening trend is real and ongoing.
- Note: Still positive (not inverted), but the direction matters as much as the level.

**VIXCLS (CBOE Volatility Index)**
- Current value: ~17.26
- Interpretation: Elevated vs. early January (~14–15) but well below crisis levels (>30). Markets are cautiously watchful — not panicked, not complacent. Consistent with SPY/QQQ at all-time highs while geopolitical and rate risks linger.

**FEDFUNDS (Federal Funds Rate)**
- Current value: 3.64% (held since February 2026)
- Fed on pause — not cutting, not hiking.
- Spread between Fed Funds (3.64%) and 10Y (4.47%) ≈ 83 bps. This spread has been widening, contributing to yield curve flattening in T10Y2Y.

### Problem Identified: Lookback Window Too Short
The 90-day window (≈88 trading days) only captures recent memory, not true historical context. Key events like the Iran war repricing (February–April 2026) fall outside or at the edge of this window. Percentiles computed over 90 days rank today against a narrow slice of its own recent history.

**Resolution for Phase 2:** Extend lookback to 252 days (1 trading year) minimum, 520 days (2 trading years) preferred. Requires `observation_start` param in FRED calls.

### Problem Identified: Signals Are Not Independent
SP500 above 200MA and VIX below 20 are highly correlated — they tend to agree at the same time. The original JS scoring effectively double-counted risk-on signals, biasing the composite score toward RISK_ON during calm equity markets.

**Resolution for Phase 2:** Compute correlation matrix across all signals. Down-weight signals that covary heavily. Signals that move independently carry more information.

---

## Phase 2 — Z-Score Normalization + Correlation Matrix (Complete)

### Goals
- Add Z-score computation alongside percentiles: `z = (current - mean) / std`
- Z-scores put all signals on the same scale (standard deviations from mean) regardless of unit differences between VIX, yield %, and spread %
- Build signal correlation matrix to identify which signals are truly independent vs. redundant
- Extend lookback to 252+ days for all series

### Expected Output Format
```
DGS10:    4.47 | pct=88.1% | z=+1.34
T10Y2Y:   0.47 | pct= 5.6% | z=-1.82
FEDFUNDS: 3.64 | pct=41.2% | z=-0.21
VIXCLS:  17.26 | pct=62.3% | z=+0.58
```

### Planned: `summarize_signals()` function
Compute percentile + z-score + mean + std for every series in a single pass. Output feeds directly into the regime classifier and eventually the covariance analysis.

---

## Phase 3 — Composite Regime Score (Complete)

### Goals
- Replace static RISK_ON / NEUTRAL / RISK_OFF / CRISIS thresholds with a weighted Z-score composite
- Weights derived from signal independence (inverse correlation)
- Stress score = weighted sum of Z-scores, with sign-adjusted for each signal's direction:
  - High VIX Z → stress up
  - High DGS10 Z → stress up  
  - Low T10Y2Y Z (flattening/inverted) → stress up
  - High FEDFUNDS Z → stress up

### Regime Boundaries (Working Hypothesis)
```
stress_score > +2.0  →  CRISIS
stress_score > +0.5  →  RISK_OFF
stress_score > -0.5  →  NEUTRAL
stress_score ≤ -0.5  →  RISK_ON
```
These boundaries will be validated against historical data in the backtesting phase.

---

## Phase 4 — Backtesting (Current)

### Goals
- Pull 5 years of FRED history
- Run regime detector across full history
- Compare regime classifications against known market events:
  - COVID crash (March 2020) → should classify CRISIS
  - 2022 rate hike cycle → should classify RISK_OFF
  - 2023–2024 bull run → should classify NEUTRAL / RISK_ON
  - Iran war shock (Feb 2026) → should classify RISK_OFF / CRISIS
- Measure: How early did the detector signal regime shifts?

### What We Built
Implemented `run_backtest()` in `agent/backtesting/backtest.py`. The approach:
1. Fetch all 5 years of history in a single API call (1826 days)
2. Slide a 252-day window across the full dataset, one trading day at a time
3. At each step: compute z-score + percentile for each signal within that window, calculate weighted stress score, classify regime
4. Output: a time series of `(date, stress_score, regime)` saved to CSV

This gives us a day-by-day regime classification we can overlay against actual market events to validate the model.

### Understanding What the Backtest Tells Us

**What's actually happening here (plain English):**

Think of the stress score like a thermometer for financial anxiety. Each day, we look back one year and ask: "Compared to the past year, how unusual are today's conditions?" We measure four things:

- **Interest rates (DGS10)** — When the government borrows money for 10 years, what do they pay? Higher = economy under pressure, borrowing is expensive, companies invest less.
- **Yield curve (T10Y2Y)** — Normally, lending money for 10 years pays more than 2 years (you want compensation for waiting). When this gap shrinks or inverts, it means investors are so worried about the near future that they're accepting lower long-term returns just for safety. Historically one of the best recession predictors.
- **Fed Funds Rate** — The rate the Federal Reserve sets overnight. When it's high, the Fed is deliberately slowing the economy to fight inflation. Money is expensive everywhere.
- **VIX** — The "fear gauge." Derived from options prices on the S&P 500. When traders are scared, they buy insurance (options), which drives VIX up. Above 30 = panic. Below 15 = complacency.

**Why z-scores matter:** A VIX of 20 means nothing in isolation. But if VIX averaged 14 over the past year with a standard deviation of 2, then 20 is a z-score of +3 — three standard deviations above normal. That's a signal. The z-score tells you "how weird is this relative to recent history."

**Why the rolling window matters:** The economy changes. A 4.5% interest rate would have been terrifying in 2021 (when rates were near zero) but unremarkable in 2007. By always comparing to the trailing year, the detector adapts — it measures *acceleration and deviation*, not absolute levels.

**The regime classifications:**
- **RISK_ON** (score ≤ -0.5): Conditions are unusually calm. Rates stable or falling, curve steep, VIX low. Good environment for growth stocks, crypto, venture bets.
- **NEUTRAL** (-0.5 to +0.5): Nothing unusual. Business as usual.
- **RISK_OFF** (+0.5 to +2.0): Stress is building. One or more signals flashing. Defensive posture — treasury bonds, cash, low-volatility assets.
- **CRISIS** (> +2.0): Multiple signals at extremes simultaneously. Rare — maybe 5-10% of trading days over 5 years. Full defensive.

### Validation Targets
When we run the backtest, we expect:
| Period | Expected Regime | Why |
|--------|----------------|-----|
| Mar 2020 | CRISIS | COVID crash — VIX hit 82, everything correlated to 1 |
| Apr–Nov 2020 | RISK_ON → NEUTRAL | Recovery, Fed at 0%, massive stimulus |
| 2022 | RISK_OFF | Fastest rate hikes in 40 years, curve inverting |
| 2023–2024 | NEUTRAL | Markets stabilized, rates plateaued |
| Feb 2026 | RISK_OFF | Iran war shock, curve flattening again |

---

## Architecture Notes

### Public (This Repo — Python)
- Generic regime detection library
- No production infrastructure references
- Clean `RegimeDetector` class with documented methodology
- Designed to be importable and extensible

### Private (JS / Lambda)
- AWS Lambda + EventBridge scheduling
- S3 persistence (`regime/latest.json`, `regime/history/`)
- USYC allocation routing
- Arc on-chain signal publishing via `AgentRegistry.sol`
- Plaid + Coinbase integration

---

## Signal Reference

| Series | Description | Risk-Off Signal |
|--------|-------------|-----------------|
| DGS10 | 10-Year Treasury Yield | High percentile (elevated rates) |
| T10Y2Y | 10Y–2Y Yield Curve Spread | Low percentile (flattening/inversion) |
| FEDFUNDS | Federal Funds Rate | High absolute level (restrictive policy) |
| VIXCLS | CBOE Volatility Index | High percentile (elevated fear) |

---

## Session Log

**2026-05-29** — First session. Built FRED data pipeline, implemented percentile scoring for DGS10 and T10Y2Y, identified 90-day window limitation, documented signal findings. Commented out classifier pending percentile-first rebuild. Identified open source / private split strategy.

**2026-06-05** — Cleanup session. Removed verbose inline comments and dead code from `run.py`. Stripped unused imports (`json`, `sys`, `fetch_series`, `classify_regime`, `on_chain`). Removed commented-out DGS10 histogram plot and the entire commented-out classifier/on-chain block. Added concise section markers and TODO breadcrumbs for Phase 2/3 resumption. Created `status_report.md` to document project progression outside of code comments.

**2026-06-26** — Backtesting session. Wired up `run_backtest()` in `agent/backtesting/backtest.py` with rolling 252-day window across 5 years of FRED data. Fixed window slicing bug (start/end were both set to same date). Outputs CSV with daily regime classifications. Next: run the backtest, validate against known market events, tune boundaries if needed.
