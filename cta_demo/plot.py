# -*- coding: utf-8 -*-
"""
plot.py —— 可视化

画三张图：
    1. 价格 + 买卖点（红涨绿跌，符合 A 股习惯）
    2. 账户资金曲线
    3. 回撤曲线
"""

import matplotlib
matplotlib.use("Agg")   # 使用非交互后端，直接存图片，不弹窗

import matplotlib.pyplot as plt

import config as cfg

# 中文字体（Windows 用微软雅黑），避免中文显示成方块
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def plot_result(df, equity_curve, trades, strategy_name, save_path="result.png"):
    fig, axes = plt.subplots(
        3, 1, figsize=(13, 11), sharex=True,
        gridspec_kw={"height_ratios": [2, 1, 1]},
    )

    # ---- 图1：价格 + 买卖点 ----
    ax = axes[0]
    ax.plot(df.index, df["close"], lw=1, color="#333", label="收盘价")
    for t in trades:
        if t["direction"] == "多":
            # 买入 = 红色上三角，卖出 = 绿色下三角
            ax.scatter(t["entry_date"], t["entry_price"], marker="^", color="red", s=60, zorder=3)
            ax.scatter(t["exit_date"], t["exit_price"], marker="v", color="green", s=60, zorder=3)
        else:
            ax.scatter(t["entry_date"], t["entry_price"], marker="v", color="green", s=60, zorder=3)
            ax.scatter(t["exit_date"], t["exit_price"], marker="^", color="red", s=60, zorder=3)
    ax.set_title(f"{strategy_name} · 价格与交易信号（▲买入 / ▼卖出）")
    ax.set_ylabel("价格")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)

    # ---- 图2：资金曲线 ----
    ax2 = axes[1]
    ax2.plot(equity_curve["date"], equity_curve["equity"], lw=1.2, color="#1f77b4", label="账户权益")
    ax2.axhline(cfg.INITIAL_CAPITAL, color="gray", ls="--", lw=0.8, label="初始资金")
    ax2.set_ylabel("权益（元）")
    ax2.legend(loc="best")
    ax2.grid(alpha=0.3)

    # ---- 图3：回撤曲线 ----
    ax3 = axes[2]
    cummax = equity_curve["equity"].cummax()
    dd = equity_curve["equity"] / cummax - 1
    ax3.fill_between(equity_curve["date"], dd * 100, 0, color="green", alpha=0.4)
    ax3.set_ylabel("回撤（%）")
    ax3.grid(alpha=0.3)
    ax3.set_xlabel("日期")

    fig.tight_layout()
    fig.savefig(save_path, dpi=120)
    plt.close(fig)
