"""
TradeRecord module: record trades with entry reasons and full strategy snapshot.

The TradeRecord class stores trades in-memory and can persist to JSON/CSV.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid
import json
import csv
import datetime as dt
import pandas as pd

@dataclass
class TradeEntry:
    id: str
    ticker: str
    entry_date: str  # ISO date
    entry_price: float
    quantity: float
    entry_reasons: List[str]
    strategy_snapshot: Dict[str, Any]
    metadata: Dict[str, Any]

    @classmethod
    def create(cls, ticker: str, entry_date: str, entry_price: float, quantity: float, entry_reasons: List[str], strategy_snapshot: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> "TradeEntry":
        return cls(
            id=str(uuid.uuid4()),
            ticker=ticker,
            entry_date=entry_date,
            entry_price=entry_price,
            quantity=quantity,
            entry_reasons=entry_reasons,
            strategy_snapshot=strategy_snapshot,
            metadata=metadata or {}
        )

class TradeRecord:
    """
    In-memory registry of trades, with persistence helpers.
    """
    def __init__(self):
        self.trades: List[TradeEntry] = []

    def add_trade(self, trade: TradeEntry) -> None:
        """Add a TradeEntry to the record."""
        self.trades.append(trade)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert stored trades to a pandas DataFrame (strategy_snapshot and reasons are JSON strings)."""
        rows = []
        for t in self.trades:
            d = asdict(t)
            d["entry_reasons"] = json.dumps(d["entry_reasons"], ensure_ascii=False)
            d["strategy_snapshot"] = json.dumps(d["strategy_snapshot"], ensure_ascii=False)
            rows.append(d)
        return pd.DataFrame(rows)

    def save_json(self, path: str) -> None:
        """Serialize to JSON array."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.trades], f, ensure_ascii=False, indent=2, default=str)

    def save_csv(self, path: str) -> None:
        """Save flattened CSV (entry_reasons and strategy_snapshot as JSON strings)."""
        df = self.to_dataframe()
        df.to_csv(path, index=False)

    def load_json(self, path: str) -> None:
        """Load trades from JSON file (replaces current trades)."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.trades = [TradeEntry(**d) for d in data]