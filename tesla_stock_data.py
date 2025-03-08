import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Initialize API client
client = ApiClient()

# Create directory for charts if it doesn't exist
if not os.path.exists('../charts'):
    os.makedirs('../charts')

# Get Tesla stock data for different time periods
time_ranges = ['1mo', '6mo', '1y', '5y', 'max']
interval_map = {'1mo': '1d', '6mo': '1d', '1y': '1wk', '5y': '1mo', 'max': '1mo'}

stock_data = {}
for time_range in time_ranges:
    # Get stock data from Yahoo Finance API
    interval = interval_map[time_range]
    data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': 'TSLA',
        'interval': interval,
        'range': time_range,
        'includeAdjustedClose': True
    })
    
    # Save raw data
    with open(f'tesla_stock_data_raw_{time_range}.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    # Process and store data
    stock_data[time_range] = data
    print(f"Retrieved Tesla stock data for {time_range} time range")

# Extract and process the most comprehensive dataset (max range)
max_data = stock_data['max']

# Check if we have valid data
if max_data and 'chart' in max_data and 'result' in max_data['chart'] and len(max_data['chart']['result']) > 0:
    result = max_data['chart']['result'][0]
    
    # Extract metadata
    meta = result['meta']
    print("\nTesla Stock Metadata:")
    print(f"Currency: {meta.get('currency', 'N/A')}")
    print(f"Symbol: {meta.get('symbol', 'N/A')}")
    print(f"Exchange Name: {meta.get('exchangeName', 'N/A')}")
    print(f"Instrument Type: {meta.get('instrumentType', 'N/A')}")
    print(f"First Trade Date: {datetime.fromtimestamp(meta.get('firstTradeDate', 0)).strftime('%Y-%m-%d') if meta.get('firstTradeDate') else 'N/A'}")
    print(f"Regular Market Price: {meta.get('regularMarketPrice', 'N/A')}")
    print(f"52 Week High: {meta.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"52 Week Low: {meta.get('fiftyTwoWeekLow', 'N/A')}")
    
    # Extract time series data
    timestamps = result['timestamp']
    quotes = result['indicators']['quote'][0]
    
    # Create a DataFrame for easier analysis
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
    
    # Save processed data to CSV
    df.to_csv('tesla_historical_prices.csv', index=False)
    print(f"\nSaved historical price data to tesla_historical_prices.csv")
    
    # Create a simple price chart
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['close'])
    plt.title('Tesla (TSLA) Historical Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.savefig('../charts/tesla_historical_price.png')
    print(f"Created historical price chart at ../charts/tesla_historical_price.png")
    
    # Calculate key financial metrics
    # 1. Monthly returns
    df['monthly_return'] = df['close'].pct_change(30)
    
    # 2. Annual returns (approximate)
    df['annual_return'] = df['close'].pct_change(365)
    
    # 3. Volatility (standard deviation of returns)
    volatility_30d = df['monthly_return'].std() * (252 ** 0.5)  # Annualized
    
    # 4. Maximum drawdown
    df['cummax'] = df['close'].cummax()
    df['drawdown'] = (df['close'] - df['cummax']) / df['cummax']
    max_drawdown = df['drawdown'].min()
    
    # Save financial metrics
    metrics = {
        'current_price': meta.get('regularMarketPrice', None),
        '52_week_high': meta.get('fiftyTwoWeekHigh', None),
        '52_week_low': meta.get('fiftyTwoWeekLow', None),
        'volatility_annualized': float(volatility_30d) if not pd.isna(volatility_30d) else None,
        'max_drawdown': float(max_drawdown) if not pd.isna(max_drawdown) else None,
        'price_change_1y': float(df['close'].iloc[-1] / df['close'].iloc[-252] - 1) if len(df) > 252 else None,
        'price_change_5y': float(df['close'].iloc[-1] / df['close'].iloc[-252*5] - 1) if len(df) > 252*5 else None
    }
    
    with open('tesla_financial_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
    
    print("\nKey Financial Metrics:")
    print(f"Current Price: ${metrics['current_price']:.2f}" if metrics['current_price'] else "Current Price: N/A")
    print(f"52 Week High: ${metrics['52_week_high']:.2f}" if metrics['52_week_high'] else "52 Week High: N/A")
    print(f"52 Week Low: ${metrics['52_week_low']:.2f}" if metrics['52_week_low'] else "52 Week Low: N/A")
    print(f"Annualized Volatility: {metrics['volatility_annualized']*100:.2f}%" if metrics['volatility_annualized'] else "Annualized Volatility: N/A")
    print(f"Maximum Drawdown: {metrics['max_drawdown']*100:.2f}%" if metrics['max_drawdown'] else "Maximum Drawdown: N/A")
    print(f"1-Year Price Change: {metrics['price_change_1y']*100:.2f}%" if metrics['price_change_1y'] else "1-Year Price Change: N/A")
    print(f"5-Year Price Change: {metrics['price_change_5y']*100:.2f}%" if metrics['price_change_5y'] else "5-Year Price Change: N/A")
    
    # Create a text summary of financial data
    with open('tesla_financial_summary.txt', 'w') as f:
        f.write("TESLA FINANCIAL DATA SUMMARY\n")
        f.write("===========================\n\n")
        f.write(f"Current Price: ${metrics['current_price']:.2f}\n" if metrics['current_price'] else "Current Price: N/A\n")
        f.write(f"52 Week High: ${metrics['52_week_high']:.2f}\n" if metrics['52_week_high'] else "52 Week High: N/A\n")
        f.write(f"52 Week Low: ${metrics['52_week_low']:.2f}\n" if metrics['52_week_low'] else "52 Week Low: N/A\n")
        f.write(f"Annualized Volatility: {metrics['volatility_annualized']*100:.2f}%\n" if metrics['volatility_annualized'] else "Annualized Volatility: N/A\n")
        f.write(f"Maximum Drawdown: {metrics['max_drawdown']*100:.2f}%\n" if metrics['max_drawdown'] else "Maximum Drawdown: N/A\n")
        f.write(f"1-Year Price Change: {metrics['price_change_1y']*100:.2f}%\n" if metrics['price_change_1y'] else "1-Year Price Change: N/A\n")
        f.write(f"5-Year Price Change: {metrics['price_change_5y']*100:.2f}%\n" if metrics['price_change_5y'] else "5-Year Price Change: N/A\n")
        
        f.write("\nData Source: Yahoo Finance\n")
        f.write(f"Data Retrieved: {datetime.now().strftime('%Y-%m-%d')}\n")
    
    print(f"\nFinancial summary saved to tesla_financial_summary.txt")
    
else:
    print("Error: Could not retrieve or process Tesla stock data")
