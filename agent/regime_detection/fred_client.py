import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "DGS10": "10-Year Treasury Yield",
    "T10Y2Y": "10Y-2Y Yield Curve",
    "FEDFUNDS": "Federal Funds Rate",
    "VIXCLS": "CBOE Volatility Index",
}


def fetch_series(series_id: str, lookback_days: int = 90) -> pd.DataFrame:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not set in environment")

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": lookback_days,
    }

    resp = requests.get(FRED_BASE_URL, params=params, timeout=10)
    resp.raise_for_status()

    observations = resp.json()["observations"]
    df = pd.DataFrame(observations)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    df = df.sort_values("date").reset_index(drop=True)

    return df[["date", "value"]]


def fetch_all(lookback_days: int = 90) -> dict[str, pd.DataFrame]:
    return {sid: fetch_series(sid, lookback_days) for sid in SERIES}
