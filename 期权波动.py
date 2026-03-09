import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. 设置深色量化风格 ---
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                               gridspec_kw={'height_ratios': [2, 1]}, facecolor='#1A1A1C')
ax1.set_facecolor('#1A1A1C')
ax2.set_facecolor('#1A1A1C')

# --- 2. 获取真实市场数据 (以标普500 SPX 和 VIX 为例) ---
print("正在从 Yahoo Finance 获取真实数据...")
# 使用过去三年的数据以展示完整的均值回归周期
data = yf.download(["^GSPC", "^VIX"], start="2023-01-01", end="2026-03-01")['Close']

# --- 3. 计算指标 ---
# 隐含波动率 (IV): 直接使用 VIX 指数
iv = data['^VIX']
# 历史波动率 (HV): 标普500过去20个交易日的年化标准差
returns = np.log(data['^GSPC'] / data['^GSPC'].shift(1))
hv = returns.rolling(window=20).std() * np.sqrt(252) * 100
# 计算偏离度 (Spread)
spread = iv - hv
df = pd.DataFrame({'IV': iv, 'HV': hv, 'Spread': spread}).dropna()

# --- 4. 绘制上方主图：IV vs HV ---
ax1.plot(df.index, df['IV'], label='Implied Volatility (VIX)', color='#5DADE2', linewidth=1.5)
ax1.plot(df.index, df['HV'], label='Historical Volatility (SPX 20D)', color='#E67E22', linewidth=1.2, alpha=0.8)
ax1.set_title('IV vs HV Historical Trends', fontsize=14, pad=15, color='white')
ax1.set_ylabel('Volatility (%)', color='#CCCCCC')
ax1.legend(loc='upper right', frameon=True, facecolor='#1A1A1C', edgecolor='gray')
ax1.grid(True, linestyle='--', alpha=0.1)

# --- 5. 绘制下方副图：Spread 均值回归信号 ---
ax2.plot(df.index, df['Spread'], color='#A569BD', linewidth=1.2, label='Volatility Spread (IV - HV)')
# 设置量化阈值线
ax2.axhline(5, color='#EC7063', linestyle='--', alpha=0.7, label='Sell IV Signal (>5%)')
ax2.axhline(-3, color='#58D68D', linestyle='--', alpha=0.7, label='Buy IV Signal (<-3%)')
ax2.axhline(2, color='white', linestyle=':', alpha=0.5, label='Mean/Exit (2%)')

# 填充极端偏离区域
ax2.fill_between(df.index, df['Spread'], 5, where=(df['Spread'] >= 5), color='#EC7063', alpha=0.3)
ax2.fill_between(df.index, df['Spread'], -3, where=(df['Spread'] <= -3), color='#58D68D', alpha=0.3)

ax2.set_title('Volatility Spread & Mean Reversion Signals', fontsize=12, color='white')
ax2.set_ylabel('Spread (%)', color='#CCCCCC')
ax2.legend(loc='lower left', fontsize=8, frameon=True, facecolor='#1A1A1C', edgecolor='gray')
ax2.grid(True, linestyle='--', alpha=0.1)

# 时间轴格式化
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.autofmt_xdate()

plt.tight_layout()
plt.savefig('iv_hv_spread_analysis.png', dpi=300)
print("分析图表已成功保存为: iv_hv_spread_analysis.png")