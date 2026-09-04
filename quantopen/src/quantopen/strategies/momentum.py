"""
Example momentum strategy.

Simple rule:
- Buy when Close crosses above MA_short and Close > MA_long
- Entry reasons include computed indicators and parameter values.
"""
from typing import Dict, Any, Tuple, List
import pandas as pd

class MomentumStrategy:
    def __init__(self, ma_short: int = 20, ma_long: int = 50, min_volume_multiplier: float = 1.0):
        """
        Initialize momentum strategy parameters.
        """
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.min_volume_multiplier = min_volume_multiplier

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a DataFrame augmented with indicators (ma_short, ma_long, vol_avg)."""
        df = df.copy()
        df["ma_short"] = df["Close"].rolling(window=self.ma_short, min_periods=1).mean()
        df["ma_long"] = df["Close"].rolling(window=self.ma_long, min_periods=1).mean()
        df["vol_avg"] = df["Volume"].rolling(window=20, min_periods=1).mean()
        return df

    def decide_buy(self, df: pd.DataFrame) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Decide whether to buy based on the latest row of df.
        Returns: (should_buy, entry_reasons, strategy_snapshot)
        """
        if len(df) < 2:
            return False, ["insufficient_data"], self._snapshot()

        df_ind = self.compute_indicators(df)
        latest = df_ind.iloc[-1]
        prev = df_ind.iloc[-2]

        reasons: List[str] = []
        # condition 1: short MA is below long MA previously and price crosses above short MA
        cross_up = (prev["Close"] < prev["ma_short"]) and (latest["Close"] > latest["ma_short"])
        condition_ma = latest["Close"] > latest["ma_long"]
        condition_vol = latest["Volume"] >= (self.min_volume_multiplier * latest["vol_avg"])

        if cross_up:
            reasons.append("price_crossed_above_ma_short")
        if condition_ma:
            reasons.append("price_above_ma_long")
        if condition_vol:
            reasons.append("volume_meets_threshold")

        should_buy = cross_up and condition_ma and condition_vol
        # Provide a detailed snapshot of indicator values
        snapshot = {
            "ma_short": float(latest["ma_short"]),
            "ma_long": float(latest["ma_long"]),
            "close": float(latest["Close"]),
            "volume": int(latest["Volume"]) if not pd.isna(latest["Volume"]) else None,
            "vol_avg": float(latest["vol_avg"]) if not pd.isna(latest["vol_avg"]) else None,
            "params": {"ma_short": self.ma_short, "ma_long": self.ma_long, "min_volume_multiplier": self.min_volume_multiplier}
        }
        if not reasons:
            reasons.append("no_buy_conditions_met")
        return should_buy, reasons, snapshot

    def _snapshot(self) -> Dict[str, Any]:
        return {"params": {"ma_short": self.ma_short, "ma_long": self.ma_long, "min_volume_multiplier": self.min_volume_multiplier}}