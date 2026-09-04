# -*- coding: utf-8 -*-
"""
main.py —— 程序入口

一条命令跑通全流程：
    加载数据 → 生成信号 → 回测 → 计算绩效 → 出图

运行：
    python main.py
"""

import pandas as pd

import config as cfg
import data_loader as dl
import strategy as st
import backtest as bt
import metrics as mt
import plot as pl


# 哪些指标用百分比显示、哪些用金额显示，方便打印
_PCT_KEYS = {"累计收益率", "年化收益率", "年化波动率", "最大回撤", "胜率"}
_MONEY_KEYS = {"初始资金", "期末权益", "平均每笔盈亏"}


def _print_metrics(metrics):
    print("\n[4] 绩效指标：")
    for k, v in metrics.items():
        if k in _PCT_KEYS:
            print(f"    {k:<14}: {v * 100:>9.2f}%")
        elif k in _MONEY_KEYS:
            print(f"    {k:<14}: {v:>12,.0f} 元")
        elif isinstance(v, int):
            print(f"    {k:<14}: {v:>12d}")
        else:
            print(f"    {k:<14}: {v:>12.4f}")


def _print_trades(trades):
    if not trades:
        print("\n    没有产生任何交易。")
        return
    df = pd.DataFrame(trades)
    df["盈亏"] = df["pnl"].map(lambda x: f"{x:,.0f}")
    show = df[["direction", "entry_date", "exit_date", "entry_price",
               "exit_price", "qty", "holding_days", "盈亏"]]
    show.columns = ["方向", "入场日期", "出场日期", "入场价", "出场价", "股数", "持有天数", "盈亏(元)"]
    print("\n[4.5] 交易明细：")
    print(show.to_string(index=False))


def main():
    print("=" * 60)
    print("  A股 CTA 趋势跟踪策略 · 学习示例")
    print("=" * 60)

    # 1) 数据
    df = dl.load_data(cfg.DATA_MODE, cfg.CSV_PATH, cfg.N_DAYS, cfg.SEED)
    print(f"\n[1] 数据加载完成：{len(df)} 根K线，"
          f"{df.index[0].date()} ~ {df.index[-1].date()}，"
          f"收盘价 {df['close'].iloc[0]:.2f} → {df['close'].iloc[-1]:.2f}")

    # 2) 策略
    if cfg.STRATEGY == "dual_ma":
        strategy = st.DualMAStrategy(cfg.FAST_MA, cfg.SLOW_MA, cfg.LONG_ONLY)
    elif cfg.STRATEGY == "donchian":
        strategy = st.DonchianStrategy(cfg.DONCHIAN_ENTRY, cfg.DONCHIAN_EXIT, cfg.LONG_ONLY)
    else:  # "donchian_atr"
        strategy = st.DonchianATRStrategy(
            cfg.DONCHIAN_ENTRY, cfg.ATR_PERIOD, cfg.ATR_STOP_MULT, cfg.LONG_ONLY
        )
    print(f"[2] 策略：{strategy.name}"
          f"（{'只做多' if cfg.LONG_ONLY else '多空双向'}）")

    # 3) 回测
    engine = bt.BacktestEngine(df, strategy)
    result = engine.run()
    print(f"[3] 回测完成：共 {len(result['trades'])} 笔交易")

    # 4) 绩效
    metrics = mt.compute_metrics(result["equity"], result["trades"],
                                 cfg.INITIAL_CAPITAL, len(df))
    _print_metrics(metrics)
    _print_trades(result["trades"])

    # 5) 出图
    pl.plot_result(df, result["equity"], result["trades"], strategy.name, "result.png")
    print(f"\n[5] 图表已保存：result.png")


if __name__ == "__main__":
    main()
