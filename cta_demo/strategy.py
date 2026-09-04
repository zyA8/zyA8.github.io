# -*- coding: utf-8 -*-
"""
strategy.py —— CTA 策略

CTA（Commodity Trading Advisor，这里泛指"趋势跟踪"）的核心理念只有一句：
    截断亏损，让利润奔跑（Cut losses short, let profits run）。

趋势策略不预测涨跌，而是"顺势而为"：涨起来就跟着做多，跌破了就撤。
靠的是少数几波大趋势赚大钱，用止损把震荡市里的小亏控制住。

这里给出两个最经典的 CTA 策略：
    1. DualMA     双均线：快线上穿慢线 → 做多；下穿 → 平仓（/做空）
    2. Donchian   唐奇安通道突破（海龟交易法）：突破 N 日新高买入，跌破 M 日新低卖出

策略的职责很单纯：只看行情，算出"目标仓位信号"（+1 做多 / 0 空仓 / -1 做空）。
真正的下单、成交、算钱，交给回测引擎（backtest.py）去做。
"""

import numpy as np
import pandas as pd

import indicators as ind


class BaseStrategy:
    """所有策略的父类，只规定一个统一接口。"""
    name = "base"

    def generate_signals(self, df):
        """
        返回一个与 df 等长的 Series：
            +1 = 满仓做多    0 = 空仓    -1 = 满仓做空

        信号在"当日收盘"产生，回测引擎会在"次日开盘"执行（避免前视偏差）。
        """
        raise NotImplementedError


class DualMAStrategy(BaseStrategy):
    """双均线趋势策略"""
    name = "双均线趋势"

    def __init__(self, fast=5, slow=20, long_only=True):
        self.fast = fast
        self.slow = slow
        self.long_only = long_only

    def generate_signals(self, df):
        fast_ma = ind.sma(df["close"], self.fast)
        slow_ma = ind.sma(df["close"], self.slow)

        # 快线在慢线上方 → 看多(+1)；下方 → 看空(-1)
        sig = pd.Series(
            np.where(fast_ma > slow_ma, 1, -1),
            index=df.index,
        )

        # 只做多模式：看空的时候不反手做空，而是保持空仓(0)
        if self.long_only:
            sig = sig.clip(lower=0)
        return sig


class DonchianStrategy(BaseStrategy):
    """唐奇安通道突破策略（海龟交易法）"""
    name = "唐奇安通道突破"

    def __init__(self, entry=20, exit_=10, long_only=True):
        self.entry = entry
        self.exit_ = exit_
        self.long_only = long_only

    def generate_signals(self, df):
        # 入场通道（周期较长）和出场通道（周期较短）分开
        upper_entry, lower_entry = ind.donchian(df, self.entry)
        upper_exit, lower_exit = ind.donchian(df, self.exit_)

        close = df["close"]
        sig = pd.Series(0, index=df.index)

        # 因为仓位是"有状态"的（要先持仓才能平仓），这里用一个简单状态机逐日推进
        pos = 0
        for i in range(len(df)):
            if pos == 0:
                # 空仓时：向上突破入场通道 → 做多
                if close.iloc[i] > upper_entry.iloc[i]:
                    pos = 1
                # 允许做空时：向下突破入场通道 → 做空
                elif (not self.long_only) and close.iloc[i] < lower_entry.iloc[i]:
                    pos = -1

            elif pos == 1:
                # 持多时：跌破出场通道下轨 → 平仓
                if close.iloc[i] < lower_exit.iloc[i]:
                    pos = 0

            elif pos == -1:
                # 持空时：涨破出场通道上轨 → 平仓
                if close.iloc[i] > upper_exit.iloc[i]:
                    pos = 0

            sig.iloc[i] = pos

        return sig


class DonchianATRStrategy(BaseStrategy):
    """
    唐奇安突破入场 + ATR 移动止损出场（经典海龟交易法的核心组合）

    入场：价格突破过去 N 日最高价 → 做多
    出场：不是等跌破通道，而是用一条"移动止损线"跟着价格往上抬：
        止损线 = 持仓期间的最高价 - K × ATR
    只要价格跌破这条线就离场。

    这样做的好处：
        - 行情一路上涨时，止损线也跟着抬高，把利润"锁住"
        - 用 ATR（真实波幅）定距离，能自适应波动大小——波动大时止损放宽，避免被洗出去
    """
    name = "唐奇安+ATR移动止损"

    def __init__(self, entry=20, atr_period=20, atr_mult=3.0, long_only=True):
        self.entry = entry
        self.atr_period = atr_period
        self.atr_mult = atr_mult
        self.long_only = long_only

    def generate_signals(self, df):
        upper_entry, lower_entry = ind.donchian(df, self.entry)
        atr = ind.atr(df, self.atr_period)

        close = df["close"]
        high = df["high"]
        low = df["low"]

        sig = pd.Series(0, index=df.index)
        pos = 0
        extreme = 0.0          # 持仓期最高价(多) / 最低价(空)

        for i in range(len(df)):
            if pos == 0:
                # 空仓：突破入场
                if close.iloc[i] > upper_entry.iloc[i]:
                    pos = 1
                    extreme = high.iloc[i]
                elif (not self.long_only) and close.iloc[i] < lower_entry.iloc[i]:
                    pos = -1
                    extreme = low.iloc[i]

            elif pos == 1:
                # 持多：不断抬升止损线
                extreme = max(extreme, high.iloc[i])
                stop = extreme - self.atr_mult * atr.iloc[i]
                if close.iloc[i] < stop:
                    pos = 0

            elif pos == -1:
                # 持空：不断压低止损线（对称逻辑）
                extreme = min(extreme, low.iloc[i])
                stop = extreme + self.atr_mult * atr.iloc[i]
                if close.iloc[i] > stop:
                    pos = 0

            sig.iloc[i] = pos

        return sig
