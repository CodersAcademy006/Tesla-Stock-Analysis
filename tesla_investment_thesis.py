import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Create directory for charts if it doesn't exist
if not os.path.exists('../charts'):
    os.makedirs('../charts')

print("Developing investment thesis for Tesla...")

# Load data from previous analyses
try:
    # Load company profile
    with open('tesla_company_profile.txt', 'r') as f:
        company_profile = f.read()
    
    # Load business model
    with open('tesla_business_model.json', 'r') as f:
        business_model = json.load(f)
    
    # Load financial metrics
    with open('tesla_financial_metrics_detailed.json', 'r') as f:
        financial_metrics = json.load(f)
    
    # Load technical metrics
    with open('tesla_technical_metrics.json', 'r') as f:
        technical_metrics = json.load(f)
    
    # Load sentiment data
    with open('tesla_sentiment_data.json', 'r') as f:
        sentiment_data = json.load(f)
    
    # Load competitor data
    with open('tesla_competitor_comparison.json', 'r') as f:
        competitor_data = json.load(f)
    
    # Load valuation results
    with open('tesla_valuation_results.json', 'r') as f:
        valuation_results = json.load(f)
    
    print("Successfully loaded data from previous analyses")
except Exception as e:
    print(f"Error loading data: {e}")

# SWOT Analysis
swot_analysis = {
    'strengths': [
        {
            'title': 'Brand Strength and Customer Loyalty',
            'description': 'Tesla has built a powerful brand with exceptional customer loyalty and advocacy. The company consistently ranks high in customer satisfaction surveys, with owners becoming brand ambassadors.'
        },
        {
            'title': 'Technology Leadership',
            'description': 'Tesla maintains leadership in key EV technologies including battery efficiency, software integration, and autonomous driving capabilities. The company\'s vertical integration allows for rapid innovation.'
        },
        {
            'title': 'Manufacturing Scale and Efficiency',
            'description': 'Tesla has rapidly scaled production capacity with Gigafactories across multiple continents. Manufacturing innovations like the Giga Press and structural battery pack improve efficiency and reduce costs.'
        },
        {
            'title': 'Supercharger Network',
            'description': 'Tesla\'s proprietary Supercharger network provides a significant competitive advantage in charging infrastructure, though the company has begun opening it to other manufacturers.'
        },
        {
            'title': 'Software and OTA Updates',
            'description': 'Tesla\'s software-first approach and over-the-air update capability allow for continuous improvement of vehicles post-purchase, adding features and fixing issues without dealer visits.'
        },
        {
            'title': 'Energy Business Integration',
            'description': 'Tesla\'s integrated energy business (solar panels, Solar Roof, Powerwall, Megapack) provides diversification and synergies with the automotive business.'
        },
        {
            'title': 'Direct Sales Model',
            'description': 'Tesla\'s direct-to-consumer sales model eliminates dealer markups, improves customer experience, and provides higher margins compared to traditional dealership models.'
        }
    ],
    'weaknesses': [
        {
            'title': 'Premium Pricing',
            'description': 'Despite price reductions, Tesla vehicles remain premium-priced products, limiting mass-market penetration in price-sensitive markets and segments.'
        },
        {
            'title': 'Limited Model Range',
            'description': 'Tesla\'s product lineup remains limited compared to traditional automakers, with gaps in certain popular segments like compact SUVs and pickup trucks (until Cybertruck reaches volume production).'
        },
        {
            'title': 'Service Network Limitations',
            'description': 'Tesla\'s service network is still developing and has faced challenges keeping pace with the rapidly growing vehicle fleet, leading to service delays in some regions.'
        },
        {
            'title': 'Quality Control Issues',
            'description': 'The company has faced criticism for inconsistent build quality and reliability issues, though improvements have been made in recent years.'
        },
        {
            'title': 'Regulatory Challenges',
            'description': 'Tesla faces ongoing regulatory scrutiny regarding its Autopilot and Full Self-Driving features, with potential for regulatory actions that could impact these key technologies.'
        },
        {
            'title': 'Executive Dependency',
            'description': 'Tesla remains closely associated with CEO Elon Musk, creating potential key person risk and distractions from his involvement with other companies (SpaceX, X/Twitter, etc.).'
        },
        {
            'title': 'Margin Pressure',
            'description': 'Recent price reductions to stimulate demand have put pressure on Tesla\'s previously industry-leading margins, raising questions about long-term profitability targets.'
        }
    ],
    'opportunities': [
        {
            'title': 'Global EV Market Growth',
            'description': 'The global EV market is projected to grow at a CAGR of 15-20% through 2030, providing a strong tailwind for Tesla\'s core business.'
        },
        {
            'title': 'Autonomous Driving Monetization',
            'description': 'Advancement of Full Self-Driving capabilities could enable robotaxi services and additional software revenue streams, potentially transforming Tesla\'s business model.'
        },
        {
            'title': 'Energy Business Expansion',
            'description': 'Tesla\'s energy generation and storage business has significant growth potential as grid-scale storage adoption increases and residential solar becomes more mainstream.'
        },
        {
            'title': 'New Markets and Models',
            'description': 'Expansion into new geographic markets and vehicle segments (particularly lower-priced models) could significantly increase Tesla\'s addressable market.'
        },
        {
            'title': 'AI and Robotics',
            'description': 'Tesla\'s investments in AI and robotics (Optimus humanoid robot) could open entirely new business lines and revenue streams beyond automotive and energy.'
        },
        {
            'title': 'Battery Technology Advancements',
            'description': 'Continued improvements in battery technology could further extend Tesla\'s competitive advantages in range, performance, and cost.'
        },
        {
            'title': 'Regulatory Tailwinds',
            'description': 'Government incentives, emissions regulations, and ICE vehicle bans in various countries create favorable conditions for EV adoption and Tesla\'s growth.'
        }
    ],
    'threats': [
        {
            'title': 'Intensifying Competition',
            'description': 'Traditional automakers and new EV startups are rapidly expanding their electric vehicle offerings, increasing competition in all segments and markets.'
        },
        {
            'title': 'Chinese Market Challenges',
            'description': 'Tesla faces strong local competition in China (a key growth market) from companies like BYD, NIO, and XPeng, along with potential regulatory and geopolitical risks.'
        },
        {
            'title': 'Supply Chain Vulnerabilities',
            'description': 'Dependency on critical materials for batteries (lithium, nickel, cobalt) creates exposure to supply constraints and price volatility.'
        },
        {
            'title': 'Macroeconomic Headwinds',
            'description': 'Economic slowdowns, inflation, and rising interest rates could impact consumer demand for premium vehicles and pressure Tesla\'s growth.'
        },
        {
            'title': 'Technological Disruption',
            'description': 'Alternative technologies (solid-state batteries, hydrogen fuel cells) could potentially disrupt Tesla\'s current technological advantages.'
        },
        {
            'title': 'Regulatory Risks',
            'description': 'Changes in EV incentives, autonomous driving regulations, or trade policies could adversely affect Tesla\'s business model and growth prospects.'
        },
        {
            'title': 'Valuation Expectations',
            'description': 'Tesla\'s premium valuation creates high expectations for growth and execution, leaving little room for disappointment or delays in new products and technologies.'
        }
    ]
}

# Key Growth Drivers and Catalysts
growth_drivers = [
    {
        'title': 'Manufacturing Capacity Expansion',
        'description': 'Continued expansion of Gigafactories in Texas, Berlin, and potential new locations will increase production capacity and enable economies of scale.',
        'impact': 'High',
        'timeline': 'Short to Medium Term'
    },
    {
        'title': 'New Vehicle Models',
        'description': 'Introduction of new models including a more affordable compact vehicle (potentially ~$25,000) would significantly expand Tesla\'s addressable market.',
        'impact': 'High',
        'timeline': 'Medium Term'
    },
    {
        'title': 'Full Self-Driving Technology',
        'description': 'Advancement of FSD capabilities toward true autonomy could enable robotaxi services and additional high-margin software revenue.',
        'impact': 'Very High',
        'timeline': 'Medium to Long Term'
    },
    {
        'title': 'Energy Business Growth',
        'description': 'Expansion of energy generation and storage business, particularly utility-scale projects and virtual power plants.',
        'impact': 'Medium',
        'timeline': 'Medium Term'
    },
    {
        'title': 'International Expansion',
        'description': 'Deeper penetration in existing markets and entry into new markets, particularly in developing economies with growing middle classes.',
        'impact': 'Medium',
        'timeline': 'Short to Medium Term'
    },
    {
        'title': 'Battery Technology Improvements',
        'description': 'Advancements in battery chemistry, cell design, and manufacturing processes to improve energy density, longevity, and reduce costs.',
        'impact': 'High',
        'timeline': 'Medium Term'
    },
    {
        'title': 'AI and Robotics',
        'description': 'Development of the Optimus humanoid robot and other AI applications could open new business lines beyond automotive.',
        'impact': 'Medium to High',
        'timeline': 'Long Term'
    }
]

# Risk Factors
risk_factors = [
    {
        'title': 'Competition Intensification',
        'description': 'Increasing competition from both traditional automakers and new EV startups could pressure market share and margins.',
        'severity': 'High',
        'probability': 'Very High'
    },
    {
        'title': 'Execution Risk',
        'description': 'Delays or challenges in ramping production of new models, expanding manufacturing capacity, or developing new technologies.',
        'severity': 'Medium',
        'probability': 'Medium'
    },
    {
        'title': 'Regulatory Challenges',
        'description': 'Potential regulatory actions regarding Autopilot/FSD, direct sales model, or changes to EV incentives.',
        'severity': 'Medium to High',
        'probability': 'Medium'
    },
    {
        'title': 'Macroeconomic Headwinds',
        'description': 'Economic slowdowns, inflation, and rising interest rates affecting consumer demand for premium vehicles.',
        'severity': 'Medium',
        'probability': 'Medium'
    },
    {
        'title': 'Supply Chain Disruptions',
        'description': 'Constraints in critical materials (lithium, nickel, cobalt) or components affecting production and costs.',
        'severity': 'Medium',
        'probability': 'Medium'
    },
    {
        'title': 'Valuation Risk',
        'description': 'Premium valuation creates high expectations, leaving little room for disappointment or delays.',
        'severity': 'High',
        'probability': 'Medium'
    },
    {
        'title': 'Key Person Risk',
        'description': 'Dependency on Elon Musk and potential distractions from his involvement with other companies.',
        'severity': 'Medium',
        'probability': 'Low to Medium'
    }
]

# Investment Recommendations by Investor Type
investor_recommendations = {
    'growth_investors': {
        'recommendation': 'Hold / Selective Buy',
        'rationale': 'Tesla offers significant long-term growth potential through expansion of its core automotive business, energy solutions, and potential new revenue streams from autonomous driving and AI. However, the current valuation appears to price in much of this growth potential, suggesting selective buying on significant pullbacks rather than aggressive accumulation.',
        'key_metrics_to_watch': [
            'Vehicle delivery growth rates',
            'Gross and operating margins',
            'Progress on Full Self-Driving technology',
            'New model introductions and production ramps',
            'Energy business revenue growth'
        ],
        'suggested_position_size': 'Moderate (3-5% of growth portfolio)',
        'time_horizon': '5+ years'
    },
    'value_investors': {
        'recommendation': 'Avoid',
        'rationale': 'Tesla\'s current valuation significantly exceeds traditional value metrics and our DCF-based intrinsic value estimates. The stock trades at premium multiples relative to both automotive and technology peers, offering limited margin of safety even under optimistic growth scenarios.',
        'key_metrics_to_watch': [
            'P/E ratio relative to growth rate (PEG ratio)',
            'Free cash flow yield',
            'Return on invested capital',
            'Debt-to-equity ratio',
            'Competitive position and market share trends'
        ],
        'suggested_position_size': 'None',
        'time_horizon': 'Revisit if valuation becomes more attractive'
    },
    'income_investors': {
        'recommendation': 'Avoid',
        'rationale': 'Tesla does not pay a dividend and is unlikely to initiate one in the foreseeable future as the company prioritizes reinvestment for growth. The stock offers no current income and significant price volatility.',
        'key_metrics_to_watch': [
            'Capital allocation priorities',
            'Free cash flow generation',
            'Statements regarding potential future dividends',
            'Share repurchase activity'
        ],
        'suggested_position_size': 'None',
        'time_horizon': 'Not applicable'
    },
    'speculative_investors': {
        'recommendation': 'Selective Buy / Trade',
        'rationale': 'Tesla\'s high volatility and strong retail investor following create trading opportunities. The stock often responds dramatically to news, product announcements, and earnings reports. Options strategies may be appropriate for sophisticated investors seeking to capitalize on volatility.',
        'key_metrics_to_watch': [
            'Technical indicators and chart patterns',
            'Short interest and institutional ownership changes',
            'Options implied volatility',
            'Sentiment indicators and news catalysts',
            'Elon Musk\'s public statements and Twitter activity'
        ],
        'suggested_position_size': 'Small to Moderate (1-3% of speculative portfolio)',
        'time_horizon': 'Variable (days to months)'
    },
    'esg_investors': {
        'recommendation': 'Buy',
        'rationale': 'Tesla\'s core mission of acceler<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>