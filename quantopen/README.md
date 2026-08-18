# QuantOpen: Open-source Quantitative Trading System

QuantOpen is an educational, open-source quantitative trading framework that provides:

- Classification display of stock asset types (sectors/industries/exchange types).
- Candlestick (K-line) chart visualization for historical price data using mplfinance and Plotly.
- A trade record module that logs each trade including the entry reasons and the complete strategy logic used to make the purchase decision.
- Example strategy implementation (momentum-based) and analysis scripts.

This project emphasizes readable architecture, standardized code annotations (docstrings and type hints), and fully open-source algorithm and visualization code.

Status: Prototype / Example implementation. Use for learning, research, and as a starting point for production systems (not production-ready on its own).

Features
- Data loader (yfinance or CSV fallback)
- Classification utilities to list and visualize asset classes
- Candlestick charts with optional technical overlays
- TradeRecord system: stores trade entries, entry reasons and strategy snapshots
- Example momentum strategy in src/strategies/momentum.py

See docs/USAGE.md for setup and examples.

License
-------
This repository is released under the MIT License (see LICENSE file).
