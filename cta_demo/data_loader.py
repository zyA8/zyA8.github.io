# -*- coding: utf-8 -*-
"""
data_loader.py —— 数据加载

默认生成"合成行情数据"（保证没有网络也能直接跑起来），
也支持读取本地 CSV 的真实行情（见 README 里的 akshare 示例）。
"""

import numpy as np
import pandas as pd


def load_data(mode="synthetic", csv_path=None, n_days=500, seed=42):
    """
    返回一个 DataFrame，必须包含四列：open / high / low / close，索引为日期。

    参数：
        mode      数据来源："synthetic" 合成 / "csv" 本地文件
        csv_path  CSV 文件路径（仅 mode="csv" 时生效）
        n_days    合成数据的天数
        seed      随机种子（固定后每次结果可复现）
    """
    if mode == "csv":
        return _load_csv(csv_path)
    return _make_synthetic(n_days, seed)


def _load_csv(path):
    """读取本地 CSV，第一列是日期，需要 open/high/low/close 四列。"""
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df = df[["open", "high", "low", "close"]]
    df = df.dropna()
    return df


def _make_synthetic(n_days, seed):
    """
    生成"趋势 + 震荡"混合的合成行情。

    设计思路：把行情切成若干段，每段随机给一个漂移方向（强趋势/弱趋势/震荡），
    这样趋势策略既有能赚钱的行情，也有会亏钱的震荡，更接近真实市场，
    而不是一路单边上涨（那会让任何策略看起来都"很神"）。
    """
    rng = np.random.default_rng(seed)

    # 交易日序列（跳过周末）
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n_days)

    opens, highs, lows, closes = [], [], [], []
    prev_close = 100.0            # 起始价格
    segment_len = 40              # 每 40 个交易日切换一次市场状态
    drift = 0.0

    # 市场状态池：(漂移, 概率)。漂移 > 0 是上升趋势，< 0 是下降，约等于 0 是震荡。
    regimes = [0.002, 0.001, 0.0005, 0.0, -0.001, -0.002]
    probs = [0.15, 0.20, 0.15, 0.20, 0.15, 0.15]

    for i in range(n_days):
        if i % segment_len == 0:
            drift = rng.choice(regimes, p=probs)

        daily_ret = drift + rng.normal(0, 0.015)   # 日波动约 1.5%
        close = prev_close * (1 + daily_ret)

        # 合成开高低收：开盘在昨收附近，高低在开收之外再外扩一点
        open_ = prev_close * (1 + rng.normal(0, 0.003))
        high = max(open_, close) * (1 + abs(rng.normal(0, 0.006)))
        low = min(open_, close) * (1 - abs(rng.normal(0, 0.006)))

        opens.append(open_)
        highs.append(high)
        lows.append(low)
        closes.append(close)

        prev_close = close

    return pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes},
        index=dates,
    )
