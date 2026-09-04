# Usage Notes for QuantOpen

Setup
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt

Basic example
- Run `python scripts/run_example.py` to:
  - fetch historical data for a sample ticker using yfinance,
  - classify the asset (sector/industry),
  - run a simple momentum strategy that may generate a buy signal,
  - record any trade taken including entry reasons and the strategy snapshot,
  - produce an interactive candlestick chart with overlays.

Trade Record
- Trade records are saved as JSON or CSV via `TradeRecord.save_json` / `save_csv`.
- Each trade contains `entry_reasons` (list of strings) and `strategy_snapshot` (dictionary of parameter values & indicators used).

Extending
- Add or replace strategies in `src/quantopen/strategies/`.
- Add visual styles or new plots in `src/quantopen/viz/`.
- Use `data_loader.fetch_price_data` for more tickers or CSV fallback data.

Security & Production
- This repository is educational. Do not use as-is for live trading without rigorous testing, risk controls, and secure credential handling.