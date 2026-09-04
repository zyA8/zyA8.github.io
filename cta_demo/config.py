# -*- coding: utf-8 -*-
"""
config.py —— 全局配置

把所有"可以调"的参数集中在这里，方便你改一个数字就对比不同结果。
"""

# ============ 资金与交易成本 ============
INITIAL_CAPITAL = 1_000_000      # 初始资金（元）
COMMISSION_RATE = 0.0003         # 佣金费率（万三，双边）
STAMP_TAX_RATE = 0.001           # 印花税（A股仅卖出收取）
SLIPPAGE = 0.0005                # 滑点（成交价与实际价的偏差，按成交额的万分之五）

# ============ A股交易规则 ============
LOT_SIZE = 100                   # 一手 = 100 股，买入必须是整手
ALLOW_SHORT = False              # 是否允许做空。个股不能做空；只有股指期货/融券/ETF期权可做空
LONG_ONLY = True                 # True = 只做多（趋势向上时持有，向下时空仓）

# ============ 回测模式 ============
STRATEGY = "dual_ma"             # 可选："dual_ma" 双均线 / "donchian" 唐奇安突破 / "donchian_atr" 唐奇安+ATR止损

# ============ 策略参数 ============
# 双均线（快线上穿慢线→做多，下穿→平仓）
FAST_MA = 5                      # 快线周期
SLOW_MA = 20                     # 慢线周期

# 唐奇安通道突破（海龟交易法）
DONCHIAN_ENTRY = 20              # 入场：突破过去 N 日最高价
DONCHIAN_EXIT = 10               # 出场：跌破过去 N 日最低价

# ATR 移动止损（用于 "donchian_atr" 策略）
ATR_PERIOD = 20                  # ATR 周期
ATR_STOP_MULT = 3.0              # 止损倍数：止损线 = 持仓最高价 - N×ATR

# ============ 数据 ============
DATA_MODE = "synthetic"          # "synthetic" = 合成行情（开箱即用）；"csv" = 读取本地CSV
CSV_PATH = "data/000300.csv"     # CSV 文件路径（需含 open/high/low/close 四列，日期为索引）
SYMBOL = "示例指数"              # 证券名称（仅用于显示）
N_DAYS = 500                     # 合成数据的天数
SEED = 5                         # 合成数据的随机种子（换一个数字=换一种市场行情）
