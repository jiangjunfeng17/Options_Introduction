import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Set advanced dark theme
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 7), facecolor='#1A1A1C')
ax.set_facecolor('#1A1A1C')

# 2. Download real market data (Past 3 years)
print("Downloading real market data from Yahoo Finance...")
start_date = "2021-01-01"
end_date = "2024-03-01"
spx = yf.download("^GSPC", start=start_date, end=end_date, progress=False) # S&P 500
vix = yf.download("^VIX", start=start_date, end=end_date, progress=False)  # VIX Index

if isinstance(spx.columns, pd.MultiIndex):
    spx.columns = spx.columns.droplevel(1)
if isinstance(vix.columns, pd.MultiIndex):
    vix.columns = vix.columns.droplevel(1)

# 3. Calculate Realized Volatility RV (20 trading days rolling, annualized)
spx['Return'] = np.log(spx['Close'] / spx['Close'].shift(1))
spx['RV'] = spx['Return'].rolling(window=20).std() * np.sqrt(252) * 100

# Merge data
df = pd.DataFrame({
    'IV': vix['Close'],
    'RV': spx['RV']
}).dropna()

# Extra: Calculate VRP explicitly for easier Excel analysis
df['VRP (IV - RV)'] = df['IV'] - df['RV']

# 4. Plot IV and RV lines
ax.plot(df.index, df['IV'], label='Implied Volatility (IV - VIX)', color='#3498DB', linewidth=1.5)
ax.plot(df.index, df['RV'], label='Realized Volatility (RV - SPX 20d)', color='#E67E22', linewidth=1.5)

# 5. Fill Variance Risk Premium (VRP)
ax.fill_between(df.index, df['IV'], df['RV'],
                where=(df['IV'] >= df['RV']),
                interpolate=True, color='#3498DB', alpha=0.3, label='Positive VRP (IV > RV) - Seller Profit Zone')
ax.fill_between(df.index, df['IV'], df['RV'],
                where=(df['IV'] < df['RV']),
                interpolate=True, color='#E67E22', alpha=0.4, label='Negative VRP (IV < RV) - Seller Loss Zone')

# 6. Chart formatting
ax.set_title('Real Market Data: Implied Volatility (IV) vs Realized Volatility (RV)', fontsize=18, color='white', pad=15)
ax.set_ylabel('Volatility (%)', fontsize=12, color='#CCCCCC')
ax.set_xlabel('Date', fontsize=12, color='#CCCCCC')
ax.tick_params(colors='#CCCCCC', labelsize=10)
ax.grid(True, linestyle='-', alpha=0.1, color='white')

# Legend setup
legend = ax.legend(loc='upper left', fontsize=11, frameon=True, facecolor='#1A1A1C', edgecolor='#333333')
for text in legend.get_texts():
    text.set_color('white')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.autofmt_xdate()

# 7. Export high-resolution image
plt.tight_layout()
plt.savefig('SP500_Real_VRP_HighRes.png', dpi=600, facecolor='#1A1A1C', edgecolor='none')
print("High-resolution chart generated: SP500_Real_VRP_HighRes.png")

# 8. Export data to CSV for Excel
csv_filename = 'SP500_VRP_Data.csv'
df.to_csv(csv_filename)
print(f"Data successfully exported for Excel: {csv_filename}")