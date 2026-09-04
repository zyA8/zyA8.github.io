# -*- coding: utf-8 -*-
"""
backtest.py —— 回测引擎

按"交易日"逐根 K 线推进，模拟真实的 下单 → 成交 → 持仓 → 平仓 过程。

执行规则（尽量贴近真实、避免自我欺骗）：
    1. 信号在 T 日收盘产生，T+1 日开盘价成交（避免前视偏差）
    2. 买入按整手（100 股）取整
    3. 买入收佣金；卖出收佣金 + 印花税；双向都算滑点
    4. 支持做空（多空双向时），空头账户按"收到卖出款、到期买回平仓"记账

引擎的职责很单纯：策略给出"目标仓位"，引擎负责撮合和记账，不关心策略怎么想。
"""

import pandas as pd

import config as cfg


class BacktestEngine:
    def __init__(self, df, strategy):
        self.df = df
        self.strategy = strategy

        self.cash = cfg.INITIAL_CAPITAL   # 现金
        self.shares = 0                   # 持仓股数（正=多头，负=空头）
        self.position = 0                 # 0 空仓 / 1 多 / -1 空

        self.entry_price = None           # 当前仓位的入场价
        self.entry_date = None            # 当前仓位的入场日期

        self.trades = []                  # 每笔"已平仓"交易的记录
        self.equity_curve = []            # 每日账户权益（资金曲线）

    # ---------- 交易成本 ----------
    @staticmethod
    def _buy_cost(price, shares):
        """买入支出 = 成交额 + 佣金 + 滑点"""
        amount = price * shares
        return amount * (1 + cfg.COMMISSION_RATE + cfg.SLIPPAGE)

    @staticmethod
    def _sell_proceeds(price, shares):
        """卖出所得 = 成交额 - 佣金 - 印花税 - 滑点"""
        amount = price * shares
        return amount * (1 - cfg.COMMISSION_RATE - cfg.STAMP_TAX_RATE - cfg.SLIPPAGE)

    def _equity(self, price):
        """账户权益 = 现金 + 持仓市值（空头为负市值）"""
        return self.cash + self.shares * price

    # ---------- 主循环 ----------
    def run(self):
        self.signals = self.strategy.generate_signals(self.df)

        for i in range(len(self.df)):
            bar = self.df.iloc[i]
            date = self.df.index[i]

            # 用"昨天收盘"产生的信号，在今天开盘价执行
            if i >= 1:
                target = int(self.signals.iloc[i - 1])
                self._rebalance(target, bar["open"], date)

            # 每天按收盘价记录一次权益
            self.equity_curve.append({"date": date, "equity": self._equity(bar["close"])})

        return self._build_result()

    def _rebalance(self, target, price, date):
        """把当前仓位调整到目标仓位（平旧仓 → 开新仓）。"""
        if target == self.position:
            return

        # 1) 平掉现有仓位
        if self.position == 1:
            self.cash += self._sell_proceeds(price, self.shares)
            self._record_trade(price, date)
        elif self.position == -1:
            self.cash -= self._buy_cost(price, -self.shares)   # 买回股票平空
            self._record_trade(price, date)

        self.shares = 0
        self.position = 0
        self.entry_price = None
        self.entry_date = None

        # 2) 建立新仓位
        if target == 1:
            n = self._max_lot_shares(price)
            self.cash -= self._buy_cost(price, n)
            self.shares = n
        elif target == -1:
            # 简化处理：卖空也按相同资金规模计算（收到卖出款）
            n = self._max_lot_shares(price)
            self.cash += self._sell_proceeds(price, n)
            self.shares = -n

        if target != 0:
            self.position = target
            self.entry_price = price
            self.entry_date = date

    def _max_lot_shares(self, price):
        """按当前现金最多能买多少股（向下取整到整手）。"""
        per_share_cost = price * (1 + cfg.COMMISSION_RATE + cfg.SLIPPAGE)
        lots = int(self.cash / (per_share_cost * cfg.LOT_SIZE))
        return lots * cfg.LOT_SIZE

    def _record_trade(self, exit_price, exit_date):
        """平仓时记录一笔交易（盈亏为毛盈亏，未扣费；净收益以权益曲线为准）。"""
        qty = self.shares
        entry = self.entry_price

        if qty > 0:
            direction = "多"
            gross_pnl = (exit_price - entry) * qty
        else:
            direction = "空"
            gross_pnl = (entry - exit_price) * (-qty)

        notional = abs(qty) * entry
        ret = gross_pnl / notional if notional else 0.0

        self.trades.append(
            {
                "direction": direction,
                "entry_date": self.entry_date,
                "exit_date": exit_date,
                "entry_price": round(entry, 2),
                "exit_price": round(exit_price, 2),
                "qty": abs(qty),
                "holding_days": (exit_date - self.entry_date).days,
                "pnl": gross_pnl,      # 毛盈亏
                "ret": ret,            # 毛收益率
            }
        )

    def _build_result(self):
        equity = pd.DataFrame(self.equity_curve)
        equity["date"] = pd.to_datetime(equity["date"])
        return {"equity": equity, "trades": self.trades}
