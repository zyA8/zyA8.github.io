"""
Candlestick (K-line) plotting utilities.

Provides:
- plot_candlestick_mpl: static mplfinance plot for quick PNGs
- plot_candlestick_plotly: interactive Plotly chart (can display in notebooks)
"""
from typing import Optional, Sequence, Dict
import pandas as pd

def ensure_df(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
    return df

def add_moving_averages(df: pd.DataFrame, windows: Sequence[int] = (20, 50)) -> pd.DataFrame:
    df = df.copy()
    for w in windows:
        df[f"ma{w}"] = df["Close"].rolling(window=w, min_periods=1).mean()
    return df

def plot_candlestick_mpl(df: pd.DataFrame, title: str = "Candlestick", ma_windows: Optional[Sequence[int]] = (20,50), save_path: Optional[str] = None) -> None:
    """
    Plot candlestick with mplfinance.
    """
    import mplfinance as mpf
    df = ensure_df(df)
    df_ma = add_moving_averages(df, ma_windows or ())
    mav = list(ma_windows) if ma_windows else None
    mpf.plot(df_ma, type='candle', style='yahoo', title=title, mav=mav, volume=True, savefig=save_path)

def plot_candlestick_plotly(df: pd.DataFrame, title: str = "Candlestick", ma_windows: Optional[Sequence[int]] = (20,50)) -> Dict:
    """
    Return a Plotly Figure dict for interactive display. Consumers can `fig.show()`.

    Returns a dictionary containing the figure object (plotly.graph_objects.Figure).
    """
    import plotly.graph_objects as go
    df = ensure_df(df)
    df_ma = add_moving_averages(df, ma_windows or ())
    fig = go.Figure(data=[
        go.Candlestick(
            x=df_ma.index,
            open=df_ma["Open"],
            high=df_ma["High"],
            low=df_ma["Low"],
            close=df_ma["Close"],
            name="Price"
        )
    ])
    for w in (ma_windows or ()):
        fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma[f"ma{w}"], name=f"MA{w}", mode='lines'))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
    return {"fig": fig}