# -*- coding: utf-8 -*-
"""
metrics.py —— 绩效指标

把回测结果算成一组"看得懂"的数字，用来判断策略好不好：
收益（累计/年化）、风险（波动率/最大回撤）、性价比（夏普/卡玛）、
以及交易质量（胜率/盈亏比）。
"""

import numpy as np


def compute_metrics(equity, trades, initial_capital, n_days, risk_free=0.02):
    eq = equity["equity"].astype(float)

    # ---- 收益 ----
    total_return = eq.iloc[-1] / initial_capital - 1
    years = n_days / 252
    annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0

    # ---- 风险 ----
    daily_ret = eq.pct_change().dropna()
    volatility = daily_ret.std() * np.sqrt(252)

    # ---- 性价比 ----
    sharpe = (daily_ret.mean() * 252 - risk_free) / volatility if volatility > 0 else 0.0

    cummax = eq.cummax()
    drawdown = eq / cummax - 1
    max_drawdown = drawdown.min()   # 负数，越小（越负）回撤越大
    calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0.0

    # ---- 交易统计 ----
    n_trades = len(trades)
    if n_trades > 0:
        pnls = [t["pnl"] for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        win_rate = len(wins) / n_trades
        profit_factor = sum(wins) / abs(sum(losses)) if sum(losses) != 0 else float("inf")
        avg_pnl = float(np.mean(pnls))
    else:
        win_rate = profit_factor = avg_pnl = 0.0

    return {
        "初始资金": float(initial_capital),
        "期末权益": float(eq.iloc[-1]),
        "累计收益率": float(total_return),
        "年化收益率": float(annual_return),
        "年化波动率": float(volatility),
        "夏普比率": float(sharpe),
        "最大回撤": float(max_drawdown),
        "卡玛比率": float(calmar),
        "交易次数": n_trades,
        "胜率": float(win_rate),
        "盈亏比(ProfitFactor)": float(profit_factor),
        "平均每笔盈亏": avg_pnl,
    }
