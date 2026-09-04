# -*- coding: utf-8 -*-
"""
indicators.py —— 技术指标

全部用 pandas 向量化实现（快、简洁、易读）。
关键点：任何"需要用到未来数据"的地方，都用 shift() 前移一格，
避免"前视偏差"（lookahead bias）——即假装自己能预知未来，这是回测最常见的坑。
"""

import pandas as pd


def sma(series, n):
    """简单移动平均：过去 n 个值的平均数。"""
    return series.rolling(n).mean()


def ema(series, n):
    """指数移动平均：越近的价格权重越大。"""
    return series.ewm(span=n, adjust=False).mean()


def atr(df, n):
    """
    平均真实波幅 ATR：衡量价格的波动幅度，常用于设置止损。

    真实波幅 TR = max(当日高低差, |最高-昨收|, |最低-昨收|)
    ATR = TR 的 n 日平均。
    """
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(n).mean()


def donchian(df, n):
    """
    唐奇安通道：过去 n 日的最高价（上轨）与最低价（下轨）。

    注意 shift(1)：用的是"截至昨天"的区间。也就是说，今天是拿
    "前 n 天（不含今天）"的最高价作上轨，今天收盘价突破它才算信号。
    如果不 shift，今天最高价会包含自己，等于偷看了当天结果。
    """
    upper = df["high"].rolling(n).max().shift(1)
    lower = df["low"].rolling(n).min().shift(1)
    return upper, lower
