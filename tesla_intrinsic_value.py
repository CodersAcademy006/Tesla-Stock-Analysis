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

print("Calculating Tesla's intrinsic value...")

# Load Tesla financial data
try:
    # Load financial metrics from our previous analysis
    with open('tesla_financial_metrics_detailed.json', 'r') as f:
        financial_metrics = json.load(f)
    
    # Load competitor data for comparison
    with open('tesla_competitor_comparison.json', 'r') as f:
        competitor_data = json.load(f)
    
    print("Loaded financial data successfully")
except Exception as e:
    print(f"Error loading financial data: {e}")
    financial_metrics = {}
    competitor_data = {}

# Current Tesla data
current_price = 284.65  # From our previous analysis
shares_outstanding = 3.16  # Billion shares
market_cap = current_price * shares_outstanding  # In billions

# Financial data for DCF model (in billions USD)
# Using data from our previous analysis and projections
historical_financials = {
    'revenue': {
        '2019': 24.58,
        '2020': 31.54,
        '2021': 53.82,
        '2022': 81.46,
        '2023': 96.77
    },
    'fcf': {  # Free Cash Flow
        '2019': 1.08,
        '2020': 2.81,
        '2021': 4.98,
        '2022': 7.57,
        '2023': 5.05
    },
    'fcf_margin': {  # FCF as percentage of revenue
        '2019': 4.39,
        '2020': 8.91,
        '2021': 9.25,
        '2022': 9.29,
        '2023': 5.22
    }
}

# Calculate historical growth rates
years = ['2019', '2020', '2021', '2022', '2023']
revenue_growth = []
fcf_growth = []

for i in range(1, len(years)):
    prev_year = years[i-1]
    curr_year = years[i]
    
    # Revenue growth
    prev_rev = historical_financials['revenue'][prev_year]
    curr_rev = historical_financials['revenue'][curr_year]
    growth = (curr_rev / prev_rev - 1) * 100
    revenue_growth.append(growth)
    
    # FCF growth
    prev_fcf = historical_financials['fcf'][prev_year]
    curr_fcf = historical_financials['fcf'][curr_year]
    growth = (curr_fcf / prev_fcf - 1) * 100
    fcf_growth.append(growth)

# Calculate average growth rates
avg_revenue_growth = sum(revenue_growth) / len(revenue_growth)
avg_fcf_growth = sum(fcf_growth) / len(fcf_growth)

print(f"Historical average revenue growth: {avg_revenue_growth:.2f}%")
print(f"Historical average FCF growth: {avg_fcf_growth:.2f}%")

# DCF Model Parameters
forecast_years = 10  # 10-year forecast period
terminal_growth_rate = 3.0  # Long-term growth rate after forecast period
discount_rates = [8.0, 10.0, 12.0]  # Different discount rates for sensitivity analysis

# Forecast scenarios
scenarios = {
    'bull': {
        'description': 'Bull Case - High Growth',
        'initial_growth': 25.0,  # Initial revenue growth rate
        'terminal_growth': 4.0,  # Terminal growth rate
        'target_fcf_margin': 12.0,  # Target FCF margin
        'discount_rate': 8.0  # Discount rate (WACC)
    },
    'base': {
        'description': 'Base Case - Moderate Growth',
        'initial_growth': 15.0,
        'terminal_growth': 3.0,
        'target_fcf_margin': 10.0,
        'discount_rate': 10.0
    },
    'bear': {
        'description': 'Bear Case - Low Growth',
        'initial_growth': 8.0,
        'terminal_growth': 2.0,
        'target_fcf_margin': 7.0,
        'discount_rate': 12.0
    }
}

# Function to calculate DCF valuation
def calculate_dcf(initial_revenue, initial_growth_rate, terminal_growth_rate, 
                  target_fcf_margin, discount_rate, forecast_years):
    
    # Initialize arrays to store forecast values
    years_forecast = list(range(1, forecast_years + 1))
    revenue_forecast = []
    fcf_forecast = []
    fcf_margin_forecast = []
    discount_factors = []
    present_values = []
    
    # Current values
    current_revenue = initial_revenue
    current_growth_rate = initial_growth_rate
    current_fcf_margin = historical_financials['fcf_margin']['2023']
    
    # Calculate growth rate decay factor
    # This will gradually reduce growth rate from initial to terminal over the forecast period
    growth_decay = (initial_growth_rate - terminal_growth_rate) / forecast_years
    
    # Calculate FCF margin improvement factor
    # This will gradually increase FCF margin from current to target over the forecast period
    margin_improvement = (target_fcf_margin - current_fcf_margin) / forecast_years
    
    # Generate forecast
    for year in years_forecast:
        # Calculate growth rate for this year (decaying over time)
        growth_rate = max(initial_growth_rate - (growth_decay * (year - 1)), terminal_growth_rate)
        
        # Calculate revenue
        revenue = current_revenue * (1 + growth_rate / 100)
        revenue_forecast.append(revenue)
        
        # Update FCF margin (improving over time)
        fcf_margin = min(current_fcf_margin + (margin_improvement * year), target_fcf_margin)
        fcf_margin_forecast.append(fcf_margin)
        
        # Calculate FCF
        fcf = revenue * (fcf_margin / 100)
        fcf_forecast.append(fcf)
        
        # Calculate discount factor
        discount_factor = 1 / ((1 + discount_rate / 100) ** year)
        discount_factors.append(discount_factor)
        
        # Calculate present value of FCF
        present_value = fcf * discount_factor
        present_values.append(present_value)
        
        # Update current revenue for next iteration
        current_revenue = revenue
    
    # Calculate terminal value
    terminal_value = fcf_forecast[-1] * (1 + terminal_growth_rate / 100) / (discount_rate / 100 - terminal_growth_rate / 100)
    
    # Calculate present value of terminal value
    terminal_value_pv = terminal_value * discount_factors[-1]
    
    # Calculate enterprise value
    enterprise_value = sum(present_values) + terminal_value_pv
    
    # Adjustments to get equity value
    cash = 29.0  # Cash and equivalents in billions
    debt = 6.3   # Total debt in billions
    equity_value = enterprise_value + cash - debt
    
    # Calculate per share value
    per_share_value = equity_value / shares_outstanding
    
    return {
        'revenue_forecast': revenue_forecast,
        'fcf_forecast': fcf_forecast,
        'fcf_margin_forecast': fcf_margin_forecast,
        'present_values': present_values,
        'terminal_value': terminal_value,
        'terminal_value_pv': terminal_value_pv,
        'enterprise_value': enterprise_value,
        'equity_value': equity_value,
        'per_share_value': per_share_value,
        'upside_potential': (per_share_value / current_price - 1) * 100
    }

# Calculate DCF for each scenario
dcf_results = {}
for scenario, params in scenarios.items():
    print(f"Calculating {params['description']}...")
    dcf_results[scenario] = calculate_dcf(
        initial_revenue=historical_financials['revenue']['2023'],
        initial_growth_rate=params['initial_growth'],
        terminal_growth_rate=params['terminal_growth'],
        target_fcf_margin=params['target_fcf_margin'],
        discount_rate=params['discount_rate'],
        forecast_years=forecast_years
    )
    
    print(f"  Intrinsic value: ${dcf_results[scenario]['per_share_value']:.2f}")
    print(f"  Upside potential: {dcf_results[scenario]['upside_potential']:.2f}%")

# Sensitivity Analysis
print("\nPerforming sensitivity analysis...")

# Create matrices for sensitivity analysis
growth_rates = np.arange(5, 26, 5)  # 5% to 25% in steps of 5%
fcf_margins = np.arange(6, 15, 2)   # 6% to 14% in steps of 2%
sensitivity_matrix = np.zeros((len(growth_rates), len(fcf_margins)))

# Calculate values for different combinations
for i, growth in enumerate(growth_rates):
    for j, margin in enumerate(fcf_margins):
        result = calculate_dcf(
            initial_revenue=historical_financials['revenue']['2023'],
            initial_growth_rate=growth,
            terminal_growth_rate=scenarios['base']['terminal_growth'],
            target_fcf_margin=margin,
            discount_rate=scenarios['base']['discount_rate'],
            forecast_years=forecast_years
        )
        sensitivity_matrix[i, j] = result['per_share_value']

# Create visualizations

# 1. DCF Valuation by Scenario
plt.figure(figsize=(10, 6))
scenarios_list = list(scenarios.keys())
values = [dcf_results[s]['per_share_value'] for s in scenarios_list]
scenario_labels = [scenarios[s]['description'] for s in scenarios_list]

bars = plt.bar(scenario_labels, values)
plt.axhline(y=current_price, color='r', linestyle='--', label=f'Current Price: ${current_price:.2f}')

# Add values on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 5,
            f'${height:.2f}', ha='center', va='bottom')

plt.title('Tesla Intrinsic Value by Scenario')
plt.ylabel('Price per Share ($)')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('../charts/tesla_dcf_scenarios.png')
print("Created DCF scenarios chart")

# 2. Sensitivity Analysis Heatmap
plt.figure(figsize=(12, 8))
plt.imshow(sensitivity_matrix, cmap='viridis', aspect='auto')
plt.colorbar(label='Intrinsic Value ($)')
plt.title('Tesla Intrinsic Value Sensitivity Analysis')
plt.xlabel('Target FCF Margin (%)')
plt.ylabel('Initial Revenue Growth Rate (%)')

# Add x and y tick labels
plt.xticks(np.arange(len(fcf_margins)), [f"{m}%" for m in fcf_margins])
plt.yticks(np.arange(len(growth_rates)), [f"{g}%" for g in growth_rates])

# Add text annotations in the heatmap cells
for i in range(len(growth_rates)):
    for j in range(len(fcf_margins)):
        plt.text(j, i, f"${sensitivity_matrix[i, j]:.0f}", 
                 ha="center", va="center", color="w" if sensitivity_matrix[i, j] < 400 else "black")

plt.tight_layout()
plt.savefig('../charts/tesla_sensitivity_analysis.png')
print("Created sensitivity analysis chart")

# 3. Forecast Revenue and FCF (Base Case)
plt.figure(figsize=(14, 7))

# Create x-axis labels (years)
forecast_years_labels = [str(year + 2023) for year in range(1, forecast_years + 1)]
historical_years = list(historical_financials['revenue'].keys())
all_years = historical_years + forecast_years_labels

# Historical and forecast revenue
historical_revenue = list(historical_financials['revenue'].values())
forecast_revenue = dcf_results['base']['revenue_forecast']
all_revenue = historical_revenue + forecast_revenue

# Historical and forecast FCF
historical_fcf = list(historical_financials['fcf'].values())
forecast_fcf = dcf_results['base']['fcf_forecast']
all_fcf = historical_fcf + forecast_fcf

# Plot revenue
plt.subplot(2, 1, 1)
plt.plot(all_years, all_revenue, marker='o', label='Revenue')
plt.axvline(x=historical_years[-1], color='r', linestyle='--', label='Forecast Start')
plt.title('Tesla Historical and Forecast Revenue (Base Case)')
plt.xlabel('Year')
plt.ylabel('Revenue ($ Billions)')
plt.grid(True, alpha=0.3)
plt.legend()

# Plot FCF
plt.subplot(2, 1, 2)
plt.plot(all_years, all_fcf, marker='o', color='green', label='Free Cash Flow')
plt.axvline(x=historical_years[-1], color='r', linestyle='--', label='Forecast Start')
plt.title('Tesla Historical and Forecast Free Cash Flow (Base Case)')
plt.xlabel('Year')
plt.ylabel('FCF ($ Billions)')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('../charts/tesla_forecast_financials.png')
print("Created forecast financials chart")

# 4. FCF Margin Forecast
plt.figure(figsize=(12, 6))

# Historical and forecast FCF margins
historical_fcf_margin = list(historical_financials['fcf_margin'].values())
forecast_fcf_margin = dcf_results['base']['fcf_margin_forecast']
all_fcf_margin = historical_fcf_margin + forecast_fcf_margin

plt.plot(all_years, all_fcf_margin, marker='o', label='FCF Margin')
plt.axvline(x=historical_years[-1], color='r', linestyle='--', label='Forecast Start')
plt.title('Tesla Historical and Forecast FCF Margin (Base Case)')
plt.xlabel('Year')
plt.ylabel('FCF Margin (%)')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig('../charts/tesla_fcf_margin_forecast.png')
print("Created FCF margin forecast chart")

# Calculate additional valuation metrics
pe_ratio = current_price / (competitor_data['TSLA']['profit_margin_pct'] / 100 * competitor_data['TSLA']['revenue_billions'] / shares_outstanding)
ps_ratio = current_price / (competitor_data['TSLA']['revenue_billions'] / shares_outstanding)
ev_to_ebitda = competitor_data['TSLA']['ev_to_ebitda']

# Comparative valuation metrics
industry_avg_pe = np.mean([competitor_data[symbol].get('pe_ratio', 0) for symbol in competitor_data if competitor_data[symbol].get('pe_ratio') is not None and symbol != 'TSLA'])
industry_avg_ps = np.mean([competitor_data[symbol].get('ps_ratio', 0) for symbol in competitor_data if competitor_data[symbol].get('ps_ratio') is not None and symbol != 'TSLA'])
industry_avg_ev_ebitda = np.mean([competitor_data[symbol].get('ev_to_ebitda', 0) for symbol in competitor_data if competitor_data[symbol].get('ev_to_ebitda') is not None and symbol != 'TSLA'])

# Create a comprehensive intrinsic value analysis text file
with open('tesla_intrinsic_value_analysis.txt', 'w') as f:
    f.write("TESLA INTRINSIC VALUE ANALYSIS\n")
    f.write("=============================\n\n")
    
    f.write("CURRENT MARKET VALUATION\n")
    f.write("----------------------\n")
    f.write(f"Current Stock Price: ${current_price:.2f}\n")
    f.write(f"Shares Outstanding: {shares_outstanding:.2f} billion\n")
    f.write(f"Market Capitalization: ${market_cap:.2f} billion\n\n")
    
    f.write("HISTORICAL FINANCIAL PERFORMANCE\n")
    f.write("------------------------------\n")
    f.write("Revenue ($ billions):\n")
    for year in historical_financials['revenue']:
        f.write(f"{year}: ${historical_financials['revenue'][year]:.2f}B\n")
    f.write(f"\nHistorical Revenue CAGR (2019-2023): {avg_revenue_growth:.2f}%\n\n")
    
    f.write("Free Cash Flow ($ billions):\n")
    for year in historical_financials['fcf']:
        f.write(f"{year}: ${historical_financials['fcf'][year]:.2f}B\n")
    f.write(f"\nHistorical FCF CAGR (2019-2023): {avg_fcf_growth:.2f}%\n\n")
    
    f.write("FCF Margin (%):\n")
    for year in historical_financials['fcf_margin']:
        f.write(f"{year}: {historical_financials['fcf_margin'][year]:.2f}%\n")
    f.write("\n")
    
    f.write("DISCOUNTED CASH FLOW VALUATION\n")
    f.write("----------------------------\n")
    f.write("We have performed a discounted cash flow (DCF) analysis using three different scenarios to estimate Tesla's intrinsic value.\n\n")
    
    for scenario, params in scenarios.items():
        f.write(f"{params['description']}:\n")
        f.write(f"  Initial Revenue Growth Rate: {params['initial_growth']:.1f}%\n")
        f.write(f"  Terminal Growth Rate: {params['terminal_growth']:.1f}%\n")
        f.write(f"  Target FCF Margin: {params['target_fcf_margin']:.1f}%\n")
        f.write(f"  Discount Rate (WACC): {params['discount_rate']:.1f}%\n")
        f.write(f"  Forecast Period: {forecast_years} years\n")
        f.write(f"  Intrinsic Value: ${dcf_results[scenario]['per_share_value']:.2f} per share\n")
        f.write(f"  Upside/Downside: {dcf_results[scenario]['upside_potential']:.2f}%\n\n")
    
    f.write("DCF Valuation Components (Base Case):\n")
    f.write(f"  Present Value of Forecast Cash Flows: ${sum(dcf_results['base']['present_values']):.2f} billion\n")
    f.write(f"  Present Value of Terminal Value: ${dcf_results['base']['terminal_value_pv']:.2f} billion\n")
    f.write(f"  Enterprise Value: ${dcf_results['base']['enterprise_value']:.2f} billion\n")
    f.write(f"  Net Cash (Cash - Debt): ${(29.0 - 6.3):.2f} billion\n")
    f.write(f"  Equity Value: ${dcf_results['base<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>