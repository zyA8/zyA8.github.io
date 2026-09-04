"""
Data loader utilities.

Primary function fetch_price_data uses yfinance and falls back to CSV if provided.
"""
from typing import Optional
import pandas as pd
import datetime as dt

try:
    import yfinance as yf
except Exception:  # pragma: no cover - allow import errors to be handled by caller
    yf = None  # type: ignore

def fetch_price_data(ticker: str, start: Optional[str] = None, end: Optional[str] = None, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch OHLCV historical price data for `ticker`.
    - Prefers yfinance
    - Returns DataFrame indexed by datetime with columns: Open, High, Low, Close, Volume

    Args:
        ticker: symbol like "AAPL" or "000001.SZ"
        start: ISO date string or None (defaults to 1y ago)
        end: ISO date string or None (defaults to today)
        interval: data interval (e.g., '1d', '1h')

    Returns:
        pandas.DataFrame
    """
    if start is None:
        start = (dt.date.today() - dt.timedelta(days=365)).isoformat()
    if end is None:
        end = dt.date.today().isoformat()

    if yf is None:
        raise RuntimeError("yfinance is not installed or failed to import. Install requirements to fetch data.")

    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(start=start, end=end, interval=interval, actions=False)
    # normalize column names, ensure OHLCV present
    df = df.rename(columns=lambda c: c.capitalize())
    expected = ["Open", "High", "Low", "Close", "Volume"]
    for col in expected:
        if col not in df.columns:
            df[col] = None
    df = df[expected]
    df.index = pd.to_datetime(df.index)
    return df