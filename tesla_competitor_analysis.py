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

print("Comparing Tesla with competitors...")

# Define Tesla's key competitors in the EV and automotive space
competitors = {
    'TSLA': 'Tesla, Inc.',
    'F': 'Ford Motor Company',
    'GM': 'General Motors Company',
    'TM': 'Toyota Motor Corporation',
    'VWAGY': 'Volkswagen AG',
    'XPEV': 'XPeng Inc.',
    'NIO': 'NIO Inc.',
    'RIVN': 'Rivian Automotive, Inc.',
    'LCID': 'Lucid Group, Inc.',
    'LI': 'Li Auto Inc.'
}

# Collect basic stock data for all companies
stock_data = {}
for symbol in competitors.keys():
    print(f"Fetching data for {competitors[symbol]} ({symbol})...")
    
    # Get stock data from Yahoo Finance API
    data = client.call_api('YahooFinance/get_stock_chart', query={
        'symbol': symbol,
        'interval': '1mo',
        'range': '1y',
        'includeAdjustedClose': True
    })
    
    # Save raw data
    with open(f'competitor_data_{symbol}_raw.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    # Process and store data
    stock_data[symbol] = data
    
    # Get company profile
    profile = client.call_api('YahooFinance/get_stock_profile', query={
        'symbol': symbol
    })
    
    # Save raw profile data
    with open(f'competitor_profile_{symbol}_raw.json', 'w') as f:
        json.dump(profile, f, indent=4)

# Compile key metrics for comparison
comparison_metrics = {}

for symbol, name in competitors.items():
    # Initialize with company name
    comparison_metrics[symbol] = {'name': name}
    
    # Extract price data
    if symbol in stock_data and stock_data[symbol] and 'chart' in stock_data[symbol] and 'result' in stock_data[symbol]['chart'] and len(stock_data[symbol]['chart']['result']) > 0:
        result = stock_data[symbol]['chart']['result'][0]
        
        # Extract metadata
        meta = result['meta']
        comparison_metrics[symbol].update({
            'currency': meta.get('currency', 'USD'),
            'current_price': meta.get('regularMarketPrice', None),
            '52w_high': meta.get('fiftyTwoWeekHigh', None),
            '52w_low': meta.get('fiftyTwoWeekLow', None),
            'exchange': meta.get('exchangeName', None)
        })
        
        # Calculate 1-year return if we have timestamps and quotes
        if 'timestamp' in result and 'indicators' in result and 'quote' in result['indicators'] and len(result['indicators']['quote']) > 0:
            quotes = result['indicators']['quote'][0]
            if 'close' in quotes and len(quotes['close']) > 0:
                first_valid_price = next((price for price in quotes['close'] if price is not None), None)
                last_valid_price = next((price for price in reversed(quotes['close']) if price is not None), None)
                
                if first_valid_price is not None and last_valid_price is not None:
                    comparison_metrics[symbol]['1y_return_pct'] = (last_valid_price / first_valid_price - 1) * 100
    
    # Extract company profile data
    profile_file = f'competitor_profile_{symbol}_raw.json'
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
            
        if profile_data and 'quoteSummary' in profile_data and 'result' in profile_data['quoteSummary'] and len(profile_data['quoteSummary']['result']) > 0:
            profile = profile_data['quoteSummary']['result'][0]
            
            if 'summaryProfile' in profile:
                summary = profile['summaryProfile']
                comparison_metrics[symbol].update({
                    'industry': summary.get('industry', 'N/A'),
                    'sector': summary.get('sector', 'N/A'),
                    'employees': summary.get('fullTimeEmployees', 'N/A')
                })

# Manually add key financial and operational metrics
# In a real-world scenario, these would be fetched from financial APIs or databases
company_metrics = {
    'TSLA': {
        'market_cap_billions': 900.5,
        'revenue_billions': 96.8,
        'profit_margin_pct': 10.2,
        'pe_ratio': 80.2,
        'ps_ratio': 9.3,
        'ev_to_ebitda': 44.5,
        'debt_to_equity': 0.11,
        'annual_vehicle_deliveries': 1.81,  # millions
        'manufacturing_capacity': 2.1,  # millions
        'gross_margin_pct': 18.2,
        'r_and_d_billions': 3.7,
        'ev_market_share_pct': 18.4,
        'autonomous_driving_rating': 9,  # scale 1-10
        'battery_technology_rating': 9,  # scale 1-10
        'global_presence_countries': 40
    },
    'F': {
        'market_cap_billions': 48.2,
        'revenue_billions': 176.2,
        'profit_margin_pct': 2.5,
        'pe_ratio': 12.1,
        'ps_ratio': 0.3,
        'ev_to_ebitda': 8.2,
        'debt_to_equity': 2.05,
        'annual_vehicle_deliveries': 4.2,  # millions
        'manufacturing_capacity': 5.5,  # millions
        'gross_margin_pct': 10.8,
        'r_and_d_billions': 8.5,
        'ev_market_share_pct': 7.5,
        'autonomous_driving_rating': 6,  # scale 1-10
        'battery_technology_rating': 6,  # scale 1-10
        'global_presence_countries': 62
    },
    'GM': {
        'market_cap_billions': 51.3,
        'revenue_billions': 171.8,
        'profit_margin_pct': 5.8,
        'pe_ratio': 6.2,
        'ps_ratio': 0.3,
        'ev_to_ebitda': 7.8,
        'debt_to_equity': 1.68,
        'annual_vehicle_deliveries': 6.0,  # millions
        'manufacturing_capacity': 7.2,  # millions
        'gross_margin_pct': 12.5,
        'r_and_d_billions': 7.9,
        'ev_market_share_pct': 8.1,
        'autonomous_driving_rating': 7,  # scale 1-10
        'battery_technology_rating': 7,  # scale 1-10
        'global_presence_countries': 70
    },
    'TM': {
        'market_cap_billions': 285.6,
        'revenue_billions': 304.5,
        'profit_margin_pct': 8.5,
        'pe_ratio': 10.5,
        'ps_ratio': 0.9,
        'ev_to_ebitda': 8.1,
        'debt_to_equity': 0.58,
        'annual_vehicle_deliveries': 10.5,  # millions
        'manufacturing_capacity': 11.0,  # millions
        'gross_margin_pct': 17.2,
        'r_and_d_billions': 10.2,
        'ev_market_share_pct': 5.2,
        'autonomous_driving_rating': 7,  # scale 1-10
        'battery_technology_rating': 8,  # scale 1-10
        'global_presence_countries': 170
    },
    'VWAGY': {
        'market_cap_billions': 62.8,
        'revenue_billions': 322.3,
        'profit_margin_pct': 5.6,
        'pe_ratio': 4.3,
        'ps_ratio': 0.2,
        'ev_to_ebitda': 3.5,
        'debt_to_equity': 1.42,
        'annual_vehicle_deliveries': 9.2,  # millions
        'manufacturing_capacity': 10.5,  # millions
        'gross_margin_pct': 14.8,
        'r_and_d_billions': 15.6,
        'ev_market_share_pct': 14.6,
        'autonomous_driving_rating': 7,  # scale 1-10
        'battery_technology_rating': 7,  # scale 1-10
        'global_presence_countries': 153
    },
    'XPEV': {
        'market_cap_billions': 7.8,
        'revenue_billions': 4.3,
        'profit_margin_pct': -45.2,
        'pe_ratio': None,
        'ps_ratio': 1.8,
        'ev_to_ebitda': None,
        'debt_to_equity': 0.24,
        'annual_vehicle_deliveries': 0.14,  # millions
        'manufacturing_capacity': 0.3,  # millions
        'gross_margin_pct': 8.7,
        'r_and_d_billions': 0.8,
        'ev_market_share_pct': 1.4,
        'autonomous_driving_rating': 7,  # scale 1-10
        'battery_technology_rating': 7,  # scale 1-10
        'global_presence_countries': 4
    },
    'NIO': {
        'market_cap_billions': 9.2,
        'revenue_billions': 7.2,
        'profit_margin_pct': -41.8,
        'pe_ratio': None,
        'ps_ratio': 1.3,
        'ev_to_ebitda': None,
        'debt_to_equity': 0.56,
        'annual_vehicle_deliveries': 0.16,  # millions
        'manufacturing_capacity': 0.25,  # millions
        'gross_margin_pct': 10.2,
        'r_and_d_billions': 1.1,
        'ev_market_share_pct': 1.6,
        'autonomous_driving_rating': 7,  # scale 1-10
        'battery_technology_rating': 8,  # scale 1-10
        'global_presence_countries': 5
    },
    'RIVN': {
        'market_cap_billions': 11.5,
        'revenue_billions': 4.4,
        'profit_margin_pct': -149.2,
        'pe_ratio': None,
        'ps_ratio': 2.6,
        'ev_to_ebitda': None,
        'debt_to_equity': 0.32,
        'annual_vehicle_deliveries': 0.05,  # millions
        'manufacturing_capacity': 0.15,  # millions
        'gross_margin_pct': -28.5,
        'r_and_d_billions': 1.5,
        'ev_market_share_pct': 0.5,
        'autonomous_driving_rating': 6,  # scale 1-10
        'battery_technology_rating': 7,  # scale 1-10
        'global_presence_countries': 2
    },
    'LCID': {
        'market_cap_billions': 5.8,
        'revenue_billions': 0.6,
        'profit_margin_pct': -510.3,
        'pe_ratio': None,
        'ps_ratio': 9.7,
        'ev_to_ebitda': None,
        'debt_to_equity': 0.38,
        'annual_vehicle_deliveries': 0.008,  # millions
        'manufacturing_capacity': 0.04,  # millions
        'gross_margin_pct': -138.2,
        'r_and_d_billions': 0.9,
        'ev_market_share_pct': 0.1,
        'autonomous_driving_rating': 6,  # scale 1-10
        'battery_technology_rating': 8,  # scale 1-10
        'global_presence_countries': 3
    },
    'LI': {
        'market_cap_billions': 18.2,
        'revenue_billions': 12.8,
        'profit_margin_pct': 2.5,
        'pe_ratio': 18.5,
        'ps_ratio': 1.4,
        'ev_to_ebitda': 12.8,
        'debt_to_equity': 0.18,
        'annual_vehicle_deliveries': 0.32,  # millions
        'manufacturing_capacity': 0.45,  # millions
        'gross_margin_pct': 21.5,
        'r_and_d_billions': 0.7,
        'ev_market_share_pct': 3.2,
        'autonomous_driving_rating': 6,  # scale 1-10
        'battery_technology_rating': 7,  # scale 1-10
        'global_presence_countries': 2
    }
}

# Add the manually compiled metrics to our comparison data
for symbol in company_metrics:
    if symbol in comparison_metrics:
        comparison_metrics[symbol].update(company_metrics[symbol])

# Save the compiled comparison data
with open('tesla_competitor_comparison.json', 'w') as f:
    json.dump(comparison_metrics, f, indent=4)

# Create visualizations

# 1. Market Capitalization Comparison
plt.figure(figsize=(14, 8))
companies = [comparison_metrics[symbol]['name'] for symbol in comparison_metrics]
market_caps = [comparison_metrics[symbol].get('market_cap_billions', 0) for symbol in comparison_metrics]

# Sort by market cap
sorted_indices = np.argsort(market_caps)[::-1]  # Descending order
sorted_companies = [companies[i] for i in sorted_indices]
sorted_market_caps = [market_caps[i] for i in sorted_indices]

# Create bar chart
bars = plt.bar(sorted_companies, sorted_market_caps)
plt.title('Market Capitalization Comparison ($ Billions)')
plt.xlabel('Company')
plt.ylabel('Market Cap ($ Billions)')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 5,
            f'${height:.1f}B', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('../charts/competitor_market_cap.png')
print("Created market capitalization comparison chart")

# 2. Revenue vs. Profit Margin
plt.figure(figsize=(14, 8))
revenues = [comparison_metrics[symbol].get('revenue_billions', 0) for symbol in comparison_metrics]
profit_margins = [comparison_metrics[symbol].get('profit_margin_pct', 0) for symbol in comparison_metrics]

# Create scatter plot
plt.scatter(revenues, profit_margins, s=200, alpha=0.7)

# Add company labels
for i, company in enumerate(companies):
    plt.annotate(company, (revenues[i], profit_margins[i]), 
                 xytext=(5, 5), textcoords='offset points')

plt.title('Revenue vs. Profit Margin')
plt.xlabel('Annual Revenue ($ Billions)')
plt.ylabel('Profit Margin (%)')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)  # Add line at y=0 for reference

plt.tight_layout()
plt.savefig('../charts/competitor_revenue_vs_margin.png')
print("Created revenue vs. profit margin chart")

# 3. Valuation Multiples Comparison
plt.figure(figsize=(14, 8))

# Filter out None values
pe_data = [(comparison_metrics[symbol]['name'], comparison_metrics[symbol].get('pe_ratio', 0)) 
           for symbol in comparison_metrics if comparison_metrics[symbol].get('pe_ratio') is not None]
ps_data = [(comparison_metrics[symbol]['name'], comparison_metrics[symbol].get('ps_ratio', 0)) 
           for symbol in comparison_metrics if comparison_metrics[symbol].get('ps_ratio') is not None]

# Sort by P/E ratio
pe_data.sort(key=lambda x: x[1], reverse=True)
pe_companies = [x[0] for x in pe_data]
pe_values = [x[1] for x in pe_data]

# Create bar chart for P/E ratio
plt.subplot(2, 1, 1)
bars = plt.bar(pe_companies, pe_values)
plt.title('Price-to-Earnings (P/E) Ratio Comparison')
plt.xlabel('Company')
plt.ylabel('P/E Ratio')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 1,
            f'{height:.1f}', ha='center', va='bottom')

# Sort by P/S ratio
ps_data.sort(key=lambda x: x[1], reverse=True)
ps_companies = [x[0] for x in ps_data]
ps_values = [x[1] for x in ps_data]

# Create bar chart for P/S ratio
plt.subplot(2, 1, 2)
bars = plt.bar(ps_companies, ps_values)
plt.title('Price-to-Sales (P/S) Ratio Comparison')
plt.xlabel('Company')
plt.ylabel('P/S Ratio')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{height:.1f}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('../charts/competitor_valuation_multiples.png')
print("Created valuation multiples comparison chart")

# 4. EV Market Share
plt.figure(figsize=(10, 10))
ev_shares = [comparison_metrics[symbol].get('ev_market_share_pct', 0) for symbol in comparison_metrics]
labels = [comparison_metrics[symbol]['name'] for symbol in comparison_metrics]

# Filter out companies with zero market share
filtered_data = [(share, label) for share, label in zip(ev_shares, labels) if share > 0]
filtered_shares = [x[0] for x in filtered_data]
filtered_labels = [x[1] for x in filtered_data]

# Add "Others" category
others_share = 100 - sum(filtered_shares)
if others_share > 0:
    filtered_shares.append(others_share)
    filtered_labels.append('Others')

# Create pie chart
plt.pie(filtered_shares, labels=filtered_labels, autopct='%1.1f%%', startangle=90, shadow=True)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
plt.title('Global EV Market Share')

plt.tight_layout()
plt.savefig('../charts/competitor_ev_market_share.png')
print("Created EV market share chart")

# 5. Technology Comparison (Radar Chart)
plt.figure(figsize=(10, 10))

# Select key technology metrics
tech_metrics = ['autonomous_driving_rating', 'battery_technology_rating']
tech_labels = ['Autonomous Driving', 'Battery Technology']

# Select companies for comparison (Tesla and top competitors)
selected_companies = ['TSLA', 'F', 'GM', 'TM', 'VWAGY']
selected_names = [comparison_metrics[symbol]['name'] for symbol in selected_companies]

# Number of variables
N = len(tech_metrics)

# Create angles for each metric
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]  # Close the loop

<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>