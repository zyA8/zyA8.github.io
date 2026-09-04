# -*- coding: utf-8 -*-
"""
sweep.py —— 参数遍历（Parameter Sweep）

把策略参数从 A 到 B 扫一遍，看"收益/夏普/回撤"如何随参数变化。

两大用途：
    1. 找大致不错的参数区间；
    2. 识别"过拟合"——如果只有孤立的一个点特别好、周围全差，多半是碰运气，
       而不是真正有效的规律（这种参数上实盘通常失效）。

运行：
    python sweep.py
会打印一张按夏普排序的参数表，并生成热力图 sweep_heatmap.png。
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as cfg
import data_loader as dl
import strategy as st
import backtest as bt
import metrics as mt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def run_one(df, strat):
    """跑一次回测，返回绩效指标字典。"""
    r = bt.BacktestEngine(df, strat).run()
    return mt.compute_metrics(r["equity"], r["trades"], cfg.INITIAL_CAPITAL, len(df))


def sweep_dual_ma(df, fast_range, slow_range):
    """遍历快线 × 慢线，返回含 fast/slow/sharpe/ret/mdd 的 DataFrame。"""
    rows = []
    for fast in fast_range:
        for slow in slow_range:
            if fast >= slow:      # 快线必须短于慢线才有意义
                continue
            m = run_one(df, st.DualMAStrategy(fast, slow, long_only=True))
            rows.append({
                "fast": fast, "slow": slow,
                "sharpe": m["夏普比率"],
                "ret": m["累计收益率"],
                "mdd": m["最大回撤"],
            })
    return pd.DataFrame(rows)


def plot_heatmap(grid, fast_range, slow_range):
    """画"慢线 × 快线"的夏普热力图。"""
    pivot = grid.pivot(index="slow", columns="fast", values="sharpe")
    pivot = pivot.reindex(index=list(slow_range), columns=list(fast_range))

    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto")
    ax.set_xticks(range(len(fast_range)))
    ax.set_xticklabels(fast_range)
    ax.set_yticks(range(len(slow_range)))
    ax.set_yticklabels(slow_range)
    ax.set_xlabel("快线周期")
    ax.set_ylabel("慢线周期")
    ax.set_title("双均线策略 · 夏普比率热力图（越绿越好，白块=无意义组合）")

    for i in range(len(slow_range)):
        for j in range(len(fast_range)):
            v = pivot.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="夏普比率")
    fig.tight_layout()
    fig.savefig("sweep_heatmap.png", dpi=120)
    plt.close(fig)
    print("\n热力图已保存：sweep_heatmap.png")


def main():
    df = dl.load_data(cfg.DATA_MODE, cfg.CSV_PATH, cfg.N_DAYS, cfg.SEED)

    fast_range = list(range(3, 16, 2))      # 3, 5, 7, 9, 11, 13, 15
    slow_range = [10, 15, 20, 30, 40, 60]

    print("=" * 62)
    print("  参数遍历：双均线（快线 × 慢线），按夏普排序")
    print("=" * 62)

    grid = sweep_dual_ma(df, fast_range, slow_range)

    show = grid.copy()
    show["收益%"] = (show["ret"] * 100).round(2)
    show["回撤%"] = (show["mdd"] * 100).round(2)
    show["夏普"] = show["sharpe"].round(2)
    top = show[["fast", "slow", "收益%", "回撤%", "夏普"]].sort_values("夏普", ascending=False)
    print(top.to_string(index=False))

    plot_heatmap(grid, fast_range, slow_range)

    print("\n提示：观察最优参数'周围'是否也普遍不错。")
    print("若最优点孤立、周围一片红，说明大概率过拟合，谨慎采用。")


if __name__ == "__main__":
    main()
