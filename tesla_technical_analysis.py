import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Initialize API client
client = ApiClient()

# Create directory for charts if it doesn't exist
if not os.path.exists('../charts'):
    os.makedirs('../charts')

print("Performing technical analysis on Tesla stock...")

# Load historical price data
try:
    df = pd.read_csv('tesla_historical_prices.csv')
    print(f"Loaded historical price data with {len(df)} records")
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by date
    df = df.sort_values('timestamp')
    
    # Set timestamp as index
    df_indexed = df.set_index('timestamp')
    
    print("Data preparation complete")
except Exception as e:
    print(f"Error loading historical price data: {e}")
    # If we can't load the data, fetch it again
    print("Fetching historical stock data...")
    
    # Get Tesla stock data for different time periods
    data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': 'TSLA',
        'interval': '1d',
        'range': '1y',
        'includeAdjustedClose': True
    })
    
    # Process the data
    if data and 'chart' in data and 'result' in data['chart'] and len(data['chart']['result']) > 0:
        result = data['chart']['result'][0]
        
        # Extract time series data
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        
        # Create a DataFrame
        df = pd.DataFrame({
            'timestamp': [datetime.fromtimestamp(ts) for ts in timestamps],
            'open': quotes['open'],
            'high': quotes['high'],
            'low': quotes['low'],
            'close': quotes['close'],
            'volume': quotes['volume']
        })
        
        # Add adjusted close if available
        if 'adjclose' in result['indicators'] and len(result['indicators']['adjclose']) > 0:
            df['adjclose'] = result['indicators']['adjclose'][0]['adjclose']
        
        # Sort by date
        df = df.sort_values('timestamp')
        
        # Set timestamp as index for calculations
        df_indexed = df.set_index('timestamp')
        
        print(f"Fetched {len(df)} days of historical price data")
    else:
        print("Error: Could not retrieve Tesla stock data")
        sys.exit(1)

# Technical Analysis

# 1. Moving Averages
print("Calculating moving averages...")
df_indexed['SMA_20'] = df_indexed['close'].rolling(window=20).mean()
df_indexed['SMA_50'] = df_indexed['close'].rolling(window=50).mean()
df_indexed['SMA_200'] = df_indexed['close'].rolling(window=200).mean()

# Exponential Moving Averages
df_indexed['EMA_12'] = df_indexed['close'].ewm(span=12, adjust=False).mean()
df_indexed['EMA_26'] = df_indexed['close'].ewm(span=26, adjust=False).mean()

# 2. MACD (Moving Average Convergence Divergence)
print("Calculating MACD...")
df_indexed['MACD'] = df_indexed['EMA_12'] - df_indexed['EMA_26']
df_indexed['MACD_Signal'] = df_indexed['MACD'].ewm(span=9, adjust=False).mean()
df_indexed['MACD_Histogram'] = df_indexed['MACD'] - df_indexed['MACD_Signal']

# 3. RSI (Relative Strength Index)
print("Calculating RSI...")
delta = df_indexed['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

# Calculate RS and RSI
rs = avg_gain / avg_loss
df_indexed['RSI'] = 100 - (100 / (1 + rs))

# 4. Bollinger Bands
print("Calculating Bollinger Bands...")
df_indexed['BB_Middle'] = df_indexed['close'].rolling(window=20).mean()
df_indexed['BB_StdDev'] = df_indexed['close'].rolling(window=20).std()
df_indexed['BB_Upper'] = df_indexed['BB_Middle'] + (df_indexed['BB_StdDev'] * 2)
df_indexed['BB_Lower'] = df_indexed['BB_Middle'] - (df_indexed['BB_StdDev'] * 2)

# 5. Support and Resistance Levels
print("Identifying support and resistance levels...")

# Function to identify local minima and maxima
def find_extrema(series, window=10):
    # Find local maxima
    maxima_indices = []
    for i in range(window, len(series) - window):
        if series.iloc[i] == max(series.iloc[i-window:i+window+1]):
            maxima_indices.append(i)
    
    # Find local minima
    minima_indices = []
    for i in range(window, len(series) - window):
        if series.iloc[i] == min(series.iloc[i-window:i+window+1]):
            minima_indices.append(i)
    
    return maxima_indices, minima_indices

# Find extrema in the price series
maxima_indices, minima_indices = find_extrema(df_indexed['close'])

# Extract resistance and support levels
resistance_levels = [df_indexed['close'].iloc[i] for i in maxima_indices]
support_levels = [df_indexed['close'].iloc[i] for i in minima_indices]

# Cluster similar levels (within 5% of each other)
def cluster_levels(levels, threshold=0.05):
    if not levels:
        return []
    
    levels = sorted(levels)
    clusters = [[levels[0]]]
    
    for level in levels[1:]:
        if level <= clusters[-1][-1] * (1 + threshold):
            clusters[-1].append(level)
        else:
            clusters.append([level])
    
    # Take average of each cluster
    return [sum(cluster) / len(cluster) for cluster in clusters]

clustered_resistance = cluster_levels(resistance_levels)
clustered_support = cluster_levels(support_levels)

# Get current price
current_price = df_indexed['close'].iloc[-1]

# Filter to relevant levels (near current price)
relevant_resistance = [level for level in clustered_resistance if level > current_price]
relevant_support = [level for level in clustered_support if level < current_price]

# Sort by distance from current price
relevant_resistance.sort()
relevant_support.sort(reverse=True)

# Take the closest 3 levels
key_resistance = relevant_resistance[:3] if len(relevant_resistance) >= 3 else relevant_resistance
key_support = relevant_support[:3] if len(relevant_support) >= 3 else relevant_support

print(f"Current price: ${current_price:.2f}")
print(f"Key resistance levels: {[f'${level:.2f}' for level in key_resistance]}")
print(f"Key support levels: {[f'${level:.2f}' for level in key_support]}")

# 6. Volume Analysis
print("Analyzing volume patterns...")
df_indexed['Volume_SMA_20'] = df_indexed['volume'].rolling(window=20).mean()
df_indexed['Volume_Ratio'] = df_indexed['volume'] / df_indexed['Volume_SMA_20']

# 7. Trend Analysis
print("Analyzing price trends...")
# Determine if price is above or below key moving averages
current_sma_20 = df_indexed['SMA_20'].iloc[-1]
current_sma_50 = df_indexed['SMA_50'].iloc[-1]
current_sma_200 = df_indexed['SMA_200'].iloc[-1]

trend_signals = []
if current_price > current_sma_20:
    trend_signals.append("Price above 20-day SMA (short-term bullish)")
else:
    trend_signals.append("Price below 20-day SMA (short-term bearish)")

if current_price > current_sma_50:
    trend_signals.append("Price above 50-day SMA (medium-term bullish)")
else:
    trend_signals.append("Price below 50-day SMA (medium-term bearish)")

if current_price > current_sma_200:
    trend_signals.append("Price above 200-day SMA (long-term bullish)")
else:
    trend_signals.append("Price below 200-day SMA (long-term bearish)")

# Check for golden cross or death cross
if df_indexed['SMA_50'].iloc[-1] > df_indexed['SMA_200'].iloc[-1] and df_indexed['SMA_50'].iloc[-20] < df_indexed['SMA_200'].iloc[-20]:
    trend_signals.append("Recent Golden Cross (50-day SMA crossed above 200-day SMA) - bullish")
elif df_indexed['SMA_50'].iloc[-1] < df_indexed['SMA_200'].iloc[-1] and df_indexed['SMA_50'].iloc[-20] > df_indexed['SMA_200'].iloc[-20]:
    trend_signals.append("Recent Death Cross (50-day SMA crossed below 200-day SMA) - bearish")

# 8. Momentum Indicators
print("Calculating momentum indicators...")
# Current RSI value
current_rsi = df_indexed['RSI'].iloc[-1]
if current_rsi > 70:
    momentum_signal = "Overbought (RSI > 70)"
elif current_rsi < 30:
    momentum_signal = "Oversold (RSI < 30)"
else:
    momentum_signal = "Neutral"

print(f"RSI: {current_rsi:.2f} - {momentum_signal}")

# MACD signal
current_macd = df_indexed['MACD'].iloc[-1]
current_macd_signal = df_indexed['MACD_Signal'].iloc[-1]
if current_macd > current_macd_signal:
    macd_signal = "Bullish (MACD above signal line)"
else:
    macd_signal = "Bearish (MACD below signal line)"

print(f"MACD: {current_macd:.2f}, Signal: {current_macd_signal:.2f} - {macd_signal}")

# Create visualizations

# 1. Price Chart with Moving Averages
print("Creating price chart with moving averages...")
plt.figure(figsize=(14, 7))
plt.plot(df_indexed.index, df_indexed['close'], label='Close Price')
plt.plot(df_indexed.index, df_indexed['SMA_20'], label='20-day SMA', alpha=0.7)
plt.plot(df_indexed.index, df_indexed['SMA_50'], label='50-day SMA', alpha=0.7)
plt.plot(df_indexed.index, df_indexed['SMA_200'], label='200-day SMA', alpha=0.7)

# Add key support and resistance levels
for level in key_support:
    plt.axhline(y=level, color='g', linestyle='--', alpha=0.5, label=f'Support ${level:.2f}')

for level in key_resistance:
    plt.axhline(y=level, color='r', linestyle='--', alpha=0.5, label=f'Resistance ${level:.2f}')

plt.title('Tesla (TSLA) Price with Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.savefig('../charts/tesla_price_with_ma.png')
print("Saved price chart with moving averages")

# 2. Bollinger Bands
print("Creating Bollinger Bands chart...")
plt.figure(figsize=(14, 7))
plt.plot(df_indexed.index, df_indexed['close'], label='Close Price')
plt.plot(df_indexed.index, df_indexed['BB_Middle'], label='20-day SMA', alpha=0.7)
plt.plot(df_indexed.index, df_indexed['BB_Upper'], label='Upper Band', alpha=0.7)
plt.plot(df_indexed.index, df_indexed['BB_Lower'], label='Lower Band', alpha=0.7)
plt.fill_between(df_indexed.index, df_indexed['BB_Upper'], df_indexed['BB_Lower'], alpha=0.1, color='blue')
plt.title('Tesla (TSLA) Bollinger Bands')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.savefig('../charts/tesla_bollinger_bands.png')
print("Saved Bollinger Bands chart")

# 3. RSI Chart
print("Creating RSI chart...")
plt.figure(figsize=(14, 5))
plt.plot(df_indexed.index, df_indexed['RSI'], label='RSI')
plt.axhline(y=70, color='r', linestyle='--', alpha=0.5)
plt.axhline(y=30, color='g', linestyle='--', alpha=0.5)
plt.fill_between(df_indexed.index, df_indexed['RSI'], 70, where=(df_indexed['RSI'] >= 70), color='r', alpha=0.3)
plt.fill_between(df_indexed.index, df_indexed['RSI'], 30, where=(df_indexed['RSI'] <= 30), color='g', alpha=0.3)
plt.title('Tesla (TSLA) Relative Strength Index')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.savefig('../charts/tesla_rsi.png')
print("Saved RSI chart")

# 4. MACD Chart
print("Creating MACD chart...")
plt.figure(figsize=(14, 5))
plt.plot(df_indexed.index, df_indexed['MACD'], label='MACD')
plt.plot(df_indexed.index, df_indexed['MACD_Signal'], label='Signal Line')
plt.bar(df_indexed.index, df_indexed['MACD_Histogram'], label='Histogram', alpha=0.5)
plt.title('Tesla (TSLA) MACD')
plt.xlabel('Date')
plt.ylabel('MACD')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.savefig('../charts/tesla_macd.png')
print("Saved MACD chart")

# 5. Volume Chart
print("Creating volume chart...")
plt.figure(figsize=(14, 5))
plt.bar(df_indexed.index, df_indexed['volume'], label='Volume', alpha=0.7)
plt.plot(df_indexed.index, df_indexed['Volume_SMA_20'], label='20-day SMA', color='r')
plt.title('Tesla (TSLA) Trading Volume')
plt.xlabel('Date')
plt.ylabel('Volume')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.savefig('../charts/tesla_volume.png')
print("Saved volume chart")

# Create a comprehensive technical analysis text file
with open('tesla_technical_analysis.txt', 'w') as f:
    f.write("TESLA TECHNICAL ANALYSIS\n")
    f.write("=======================\n\n")
    
    f.write("PRICE LEVELS\n")
    f.write("-----------\n")
    f.write(f"Current Price: ${current_price:.2f}\n\n")
    
    f.write("Key Resistance Levels:\n")
    for i, level in enumerate(key_resistance, 1):
        f.write(f"{i}. ${level:.2f}\n")
    
    f.write("\nKey Support Levels:\n")
    for i, level in enumerate(key_support, 1):
        f.write(f"{i}. ${level:.2f}\n\n")
    
    f.write("MOVING AVERAGES\n")
    f.write("---------------\n")
    f.write(f"20-day SMA: ${current_sma_20:.2f}\n")
    f.write(f"50-day SMA: ${current_sma_50:.2f}\n")
    f.write(f"200-day SMA: ${current_sma_200:.2f}\n\n")
    
    f.write("TREND ANALYSIS\n")
    f.write("--------------\n")
    for signal in trend_signals:
        f.write(f"- {signal}\n")
    f.write("\n")
    
    f.write("MOMENTUM INDICATORS\n")
    f.write("-------------------\n")
    f.write(f"RSI (14): {current_rsi:.2f} - {momentum_signal}\n")
    f.write(f"MACD: {current_macd:.2f}, Signal Line: {current_macd_signal:.2f} - {macd_signal}\n\n")
    
    f.write("BOLLINGER BANDS\n")
    f.write("--------------\n")
    f.write(f"Upper Band: ${df_indexed['BB_Upper'].iloc[-1]:.2f}\n")
    f.write(f"Middle Band: ${df_indexed['BB_Middle'].iloc[-1]:.2f}\n")
    f.write(f"Lower Band: ${df_indexed['BB_Lower'].iloc[-1]:.2f}\n\n")
    
    # Determine if price is near bands
    if current_price > df_indexed['BB_Upper'].iloc[-1] * 0.95:
        f.write("Price is near or above upper Bollinger Band, suggesting potential overbought conditions.\n\n")
    elif current_price < df_indexed['BB_Lower'].iloc[-1] * 1.05:
        f.write("Price is near or below lower Bollinger Band, suggesting potential oversold conditions.\n\n")
    else:
        f.write("Price is within Bollinger Bands, suggesting normal volatility.\n\n")
    
    f.write("VOLUME ANALYSIS\n")
    f.write("--------------\n")
    recent_volume_ratio = df_indexed['Volume_Ratio'].iloc[-1]
    avg_volume = df_indexed['Volume_SMA_20'].iloc[-1]
    f.write(f"20-day Average Volume: {avg_volume:,.0f} shares\n")
    f.write(f"Recent Volume Ratio: {recent_volume_ratio:.2f}x average\n\n")
    
    if recent_volume_ratio > 1.5:
        f.write("Recent trading volume is significantly above average, indicating strong interest.\n\n")
    elif recent_volume_ratio < 0.7:
        f.write("Recent trading volume is below average, indicating potential lack of interest.\n\n")
    else:
        f.write("Recent trading volume is near average levels.\n\n")
    
    f.write("CHART PATTERNS\n")
    f.write("-------------\n")
    # Check for potential head and shoulders pattern (simplified)
    # This is a very basic check and would need more sophisticated analysis for accuracy
    recent_highs = df_indexed['high'].iloc[-60:].rolling(window=10).max()
    if len(recent_highs.dropna()) >= 3:
        potential_pattern = "Potential head and shoulders pattern may be forming, which could indicate a reversal if confirmed."
        f.write(f"{potential_pattern}\n\n")
    else:
        f.write("No clear chart patterns identified in recent price action.\n\n")
    
    f.write("TECHNICAL OUTLOOK\n")
    f.write("----------------\n")
    
    # Determine overall technical outlook based on indicators
    bullish_signals = 0
    bearish_signals = 0
    
    # Moving averages
    if current_price > current_sma_20:
        bullish_signals += 1
    else:
        bearish_signals += 1
        
    if current_price > current_sma_50:
        bullish_signals += 1
    else:
        bearish_signals += 1
        
    if current_price > current_sma_200:
        bullish_signals += 1
    else:
        bearish_signals += 1
    
    # RSI
    if current_rsi > 50:
        bullish_signals += 1
    else:
        bearish_signals += 1
        
    # MACD
    if current_macd > current_macd_signal:
        bullish_signals += 1
    else:
        bearish_signals += 1
 <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>