"""
End-to-end example:
- fetch data for a ticker
- classify ticker
- run momentum strategy
- record a trade when buy signal occurs
- plot candlestick chart

This script is intentionally straightforward so you can see end-to-end flow.
"""
from quantopen.data_loader import fetch_price_data
from quantopen.classification import classify_ticker
from quantopen.strategies.momentum import MomentumStrategy
from quantopen.trade_record import TradeRecord, TradeEntry
from quantopen.viz.candles import plot_candlestick_plotly
import datetime as dt
import argparse

def main(ticker: str = "AAPL", start: str = None, end: str = None):
    print(f"Fetching data for {ticker}...")
    df = fetch_price_data(ticker, start=start, end=end)
    print(f"Rows fetched: {len(df)}")

    print("Classifying ticker...")
    meta = classify_ticker(ticker)
    print("Classification:", meta)

    strat = MomentumStrategy(ma_short=20, ma_long=50, min_volume_multiplier=1.0)
    should_buy, reasons, snapshot = strat.decide_buy(df)
    print("Buy decision:", should_buy)
    print("Entry reasons:", reasons)
    print("Strategy snapshot:", snapshot)

    record = TradeRecord()
    if should_buy:
        latest = df.iloc[-1]
        trade = TradeEntry.create(
            ticker=ticker,
            entry_date=latest.name.isoformat(),
            entry_price=float(latest["Close"]),
            quantity=1.0,
            entry_reasons=reasons,
            strategy_snapshot=snapshot,
            metadata={"classification": meta}
        )
        record.add_trade(trade)
        record.save_json(f"trade_record_{ticker}_{dt.date.today().isoformat()}.json")
        record.save_csv(f"trade_record_{ticker}_{dt.date.today().isoformat()}.csv")
        print("Trade recorded and saved.")
    else:
        print("No trade recorded (no buy signal).")

    # Plot interactive chart (returns a dict with figure)
    figdict = plot_candlestick_plotly(df, title=f"{ticker} candlestick")
    fig = figdict["fig"]
    try:
        fig.show()
    except Exception:
        print("Plot generated; in non-interactive environment, please run in a notebook to view it.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run QuantOpen example flow.")
    parser.add_argument("--ticker", type=str, default="AAPL")
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()
    main(ticker=args.ticker, start=args.start, end=args.end)