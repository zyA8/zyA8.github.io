"""
Classification utilities: display asset classes (sector/industry/exchange) for tickers.

This uses yfinance Ticker.info where available. For large lists, users should maintain a local mapping CSV.
"""
from typing import Dict, List, Tuple
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None  # type: ignore

def classify_ticker(ticker: str) -> Dict[str, str]:
    """
    Return a small classification dict for the ticker: sector, industry, exchange.
    If yfinance info not available, returns empty strings.

    Example:
    >>> classify_ticker("AAPL")
    {"sector": "Technology", "industry": "Consumer Electronics", "exchange": "NASDAQ"}
    """
    info = {}
    if yf is None:
        return {"sector": "", "industry": "", "exchange": "", "shortName": "", "longName": ""}

    try:
        t = yf.Ticker(ticker)
        meta = t.info or {}
        info = {
            "sector": meta.get("sector", ""),
            "industry": meta.get("industry", ""),
            "exchange": meta.get("exchange", ""),
            "shortName": meta.get("shortName", ""),
            "longName": meta.get("longName", ""),
        }
    except Exception:
        info = {"sector": "", "industry": "", "exchange": "", "shortName": "", "longName": ""}
    return info

def classify_many(tickers: List[str]) -> pd.DataFrame:
    """
    Classify multiple tickers and return a DataFrame with columns:
    ticker, sector, industry, exchange, shortName, longName
    """
    rows = []
    for t in tickers:
        meta = classify_ticker(t)
        row = {"ticker": t}
        row.update(meta)
        rows.append(row)
    return pd.DataFrame(rows)