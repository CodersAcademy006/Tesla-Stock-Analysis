import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import re
from collections import Counter

# Initialize API client
client = ApiClient()

# Create directory for charts if it doesn't exist
if not os.path.exists('../charts'):
    os.makedirs('../charts')

print("Analyzing market sentiment for Tesla...")

# 1. Get analyst ratings and insights from Yahoo Finance
tesla_insights = client.call_api('YahooFinance/get_stock_insights', query={'symbol': 'TSLA'})

# Save raw data
with open('tesla_insights_raw.json', 'w') as f:
    json.dump(tesla_insights, f, indent=4)

# 2. Get analyst reports from Yahoo Finance
tesla_analyst_reports = client.call_api('YahooFinance/get_stock_what_analyst_are_saying', query={'symbol': 'TSLA'})

# Save raw data
with open('tesla_analyst_reports_raw.json', 'w') as f:
    json.dump(tesla_analyst_reports, f, indent=4)

# 3. Get insider trading information
tesla_holders = client.call_api('YahooFinance/get_stock_holders', query={'symbol': 'TSLA'})

# Save raw data
with open('tesla_holders_raw.json', 'w') as f:
    json.dump(tesla_holders, f, indent=4)

# 4. Get recent SEC filings
tesla_sec_filings = client.call_api('YahooFinance/get_stock_sec_filing', query={'symbol': 'TSLA'})

# Save raw data
with open('tesla_sec_filings_raw.json', 'w') as f:
    json.dump(tesla_sec_filings, f, indent=4)

# 5. Get social media sentiment from Twitter
twitter_tesla = client.call_api('Twitter/search_twitter', query={
    'query': 'TSLA OR Tesla stock',
    'count': 100,
    'type': 'Latest'
})

# Save raw data
with open('tesla_twitter_raw.json', 'w') as f:
    json.dump(twitter_tesla, f, indent=4)

# Process analyst insights
analyst_insights = {}
if tesla_insights and 'finance' in tesla_insights and 'result' in tesla_insights['finance']:
    result = tesla_insights['finance']['result']
    
    # Technical events
    if 'instrumentInfo' in result and 'technicalEvents' in result['instrumentInfo']:
        tech_events = result['instrumentInfo']['technicalEvents']
        analyst_insights['technical_events'] = {
            'short_term': {
                'direction': tech_events.get('shortTermOutlook', {}).get('direction', 'N/A'),
                'score': tech_events.get('shortTermOutlook', {}).get('score', 'N/A'),
                'description': tech_events.get('shortTermOutlook', {}).get('scoreDescription', 'N/A')
            },
            'intermediate_term': {
                'direction': tech_events.get('intermediateTermOutlook', {}).get('direction', 'N/A'),
                'score': tech_events.get('intermediateTermOutlook', {}).get('score', 'N/A'),
                'description': tech_events.get('intermediateTermOutlook', {}).get('scoreDescription', 'N/A')
            },
            'long_term': {
                'direction': tech_events.get('longTermOutlook', {}).get('direction', 'N/A'),
                'score': tech_events.get('longTermOutlook', {}).get('score', 'N/A'),
                'description': tech_events.get('longTermOutlook', {}).get('scoreDescription', 'N/A')
            }
        }
    
    # Key technicals
    if 'instrumentInfo' in result and 'keyTechnicals' in result['instrumentInfo']:
        key_tech = result['instrumentInfo']['keyTechnicals']
        analyst_insights['key_technicals'] = {
            'support': key_tech.get('support', 'N/A'),
            'resistance': key_tech.get('resistance', 'N/A'),
            'stop_loss': key_tech.get('stopLoss', 'N/A')
        }
    
    # Valuation
    if 'instrumentInfo' in result and 'valuation' in result['instrumentInfo']:
        valuation = result['instrumentInfo']['valuation']
        analyst_insights['valuation'] = {
            'description': valuation.get('description', 'N/A'),
            'discount': valuation.get('discount', 'N/A'),
            'relative_value': valuation.get('relativeValue', 'N/A')
        }
    
    # Company snapshot
    if 'companySnapshot' in result:
        snapshot = result['companySnapshot']
        if 'company' in snapshot:
            analyst_insights['company_metrics'] = {
                'innovativeness': snapshot['company'].get('innovativeness', 'N/A'),
                'hiring': snapshot['company'].get('hiring', 'N/A'),
                'sustainability': snapshot['company'].get('sustainability', 'N/A'),
                'insider_sentiments': snapshot['company'].get('insiderSentiments', 'N/A'),
                'earnings_reports': snapshot['company'].get('earningsReports', 'N/A'),
                'dividends': snapshot['company'].get('dividends', 'N/A')
            }
    
    # Recommendation
    if 'recommendation' in result:
        rec = result['recommendation']
        analyst_insights['recommendation'] = {
            'rating': rec.get('rating', 'N/A'),
            'target_price': rec.get('targetPrice', 'N/A')
        }
    
    # Significant developments
    if 'sigDevs' in result:
        analyst_insights['significant_developments'] = [
            {'headline': dev.get('headline', 'N/A'), 'date': dev.get('date', 'N/A')}
            for dev in result.get('sigDevs', [])
        ]

# Process analyst reports
analyst_reports = []
if tesla_analyst_reports and 'result' in tesla_analyst_reports:
    for item in tesla_analyst_reports['result']:
        if 'hits' in item:
            for hit in item['hits']:
                report = {
                    'title': hit.get('report_title', 'N/A'),
                    'provider': hit.get('provider', 'N/A'),
                    'author': hit.get('author', 'N/A'),
                    'date': datetime.fromtimestamp(hit.get('report_date', 0)).strftime('%Y-%m-%d') if hit.get('report_date') else 'N/A',
                    'abstract': hit.get('abstract', 'N/A')
                }
                analyst_reports.append(report)

# Process insider trading
insider_trades = []
if tesla_holders and 'quoteSummary' in tesla_holders and 'result' in tesla_holders['quoteSummary']:
    for result in tesla_holders['quoteSummary']['result']:
        if 'insiderHolders' in result and 'holders' in result['insiderHolders']:
            for holder in result['insiderHolders']['holders']:
                trade = {
                    'name': holder.get('name', 'N/A'),
                    'relation': holder.get('relation', 'N/A'),
                    'transaction': holder.get('transactionDescription', 'N/A'),
                    'date': holder.get('latestTransDate', {}).get('fmt', 'N/A'),
                    'shares': holder.get('positionDirect', {}).get('fmt', 'N/A')
                }
                insider_trades.append(trade)

# Process SEC filings
sec_filings = []
if tesla_sec_filings and 'quoteSummary' in tesla_sec_filings and 'result' in tesla_sec_filings['quoteSummary']:
    for result in tesla_sec_filings['quoteSummary']['result']:
        if 'secFilings' in result and 'filings' in result['secFilings']:
            for filing in result['secFilings']['filings'][:10]:  # Get the 10 most recent filings
                sec_filing = {
                    'date': filing.get('date', 'N/A'),
                    'type': filing.get('type', 'N/A'),
                    'title': filing.get('title', 'N/A'),
                    'url': filing.get('edgarUrl', 'N/A')
                }
                sec_filings.append(sec_filing)

# Process Twitter sentiment
twitter_data = []
sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

# Simple sentiment analysis function
def analyze_sentiment(text):
    # List of positive and negative words related to stocks
    positive_words = ['buy', 'bullish', 'up', 'growth', 'profit', 'gain', 'positive', 'strong', 'good', 'great', 'excellent', 'outperform', 'beat', 'exceed', 'rise', 'rising', 'higher', 'rally', 'boom', 'success', 'successful', 'impressive', 'innovation', 'innovative', 'potential', 'opportunity', 'opportunities', 'promising', 'leader', 'leading']
    
    negative_words = ['sell', 'bearish', 'down', 'decline', 'loss', 'negative', 'weak', 'bad', 'poor', 'terrible', 'underperform', 'miss', 'fall', 'falling', 'lower', 'crash', 'bust', 'failure', 'fail', 'disappointing', 'overvalued', 'risk', 'risky', 'trouble', 'problem', 'concern', 'worried', 'worry', 'fear', 'bubble']
    
    text = text.lower()
    
    # Count occurrences of positive and negative words
    positive_count = sum(1 for word in positive_words if re.search(r'\b' + word + r'\b', text))
    negative_count = sum(1 for word in negative_words if re.search(r'\b' + word + r'\b', text))
    
    # Determine sentiment based on counts
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

if twitter_tesla and 'result' in twitter_tesla and 'timeline' in twitter_tesla['result']:
    if 'instructions' in twitter_tesla['result']['timeline']:
        for instruction in twitter_tesla['result']['timeline']['instructions']:
            if 'entries' in instruction:
                for entry in instruction['entries']:
                    if 'content' in entry and 'items' in entry['content']:
                        for item in entry['content']['items']:
                            if 'item' in item and 'itemContent' in item['item']:
                                content = item['item']['itemContent']
                                if 'tweet_results' in content and 'result' in content['tweet_results']:
                                    tweet_result = content['tweet_results']['result']
                                    if 'legacy' in tweet_result:
                                        tweet_text = tweet_result['legacy'].get('full_text', '')
                                        if tweet_text:
                                            sentiment = analyze_sentiment(tweet_text)
                                            sentiment_counts[sentiment] += 1
                                            twitter_data.append({
                                                'text': tweet_text,
                                                'sentiment': sentiment,
                                                'created_at': tweet_result['legacy'].get('created_at', 'N/A')
                                            })

# Save processed data
sentiment_data = {
    'analyst_insights': analyst_insights,
    'analyst_reports': analyst_reports,
    'insider_trades': insider_trades,
    'sec_filings': sec_filings,
    'twitter_sentiment': {
        'counts': sentiment_counts,
        'tweets': twitter_data[:20]  # Include a sample of tweets
    }
}

with open('tesla_sentiment_data.json', 'w') as f:
    json.dump(sentiment_data, f, indent=4)

# Create visualizations

# 1. Twitter Sentiment Pie Chart
if sum(sentiment_counts.values()) > 0:
    plt.figure(figsize=(10, 6))
    plt.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%', 
            colors=['green', 'red', 'gray'], startangle=90)
    plt.title('Tesla Twitter Sentiment Analysis')
    plt.axis('equal')
    plt.savefig('../charts/tesla_twitter_sentiment.png')
    print("Created Twitter sentiment chart")

# 2. Analyst Outlook Chart
if analyst_insights and 'technical_events' in analyst_insights:
    tech_events = analyst_insights['technical_events']
    
    # Convert direction to numeric score for visualization
    direction_to_score = {'NEUTRAL': 0, 'DOWN': -1, 'UP': 1}
    
    terms = ['short_term', 'intermediate_term', 'long_term']
    scores = [direction_to_score.get(tech_events[term]['direction'], 0) for term in terms]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(terms, scores, color=['blue' if s > 0 else 'red' if s < 0 else 'gray' for s in scores])
    
    # Add labels above bars
    for bar, term in zip(bars, terms):
        direction = tech_events[term]['direction']
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                direction, ha='center', va='bottom')
    
    plt.title('Tesla Technical Outlook')
    plt.ylabel('Direction (Up = 1, Neutral = 0, Down = -1)')
    plt.ylim(-1.5, 1.5)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.savefig('../charts/tesla_technical_outlook.png')
    print("Created technical outlook chart")

# Create a comprehensive market sentiment analysis text file
with open('tesla_market_sentiment.txt', 'w') as f:
    f.write("TESLA MARKET SENTIMENT ANALYSIS\n")
    f.write("===============================\n\n")
    
    # Analyst Insights
    f.write("ANALYST INSIGHTS\n")
    f.write("--------------\n")
    if analyst_insights:
        if 'recommendation' in analyst_insights:
            f.write(f"Overall Recommendation: {analyst_insights['recommendation'].get('rating', 'N/A')}\n")
            f.write(f"Price Target: ${analyst_insights['recommendation'].get('target_price', 'N/A')}\n\n")
        
        if 'technical_events' in analyst_insights:
            f.write("Technical Outlook:\n")
            tech = analyst_insights['technical_events']
            f.write(f"  Short-term: {tech['short_term']['direction']} ({tech['short_term']['description']})\n")
            f.write(f"  Intermediate-term: {tech['intermediate_term']['direction']} ({tech['intermediate_term']['description']})\n")
            f.write(f"  Long-term: {tech['long_term']['direction']} ({tech['long_term']['description']})\n\n")
        
        if 'key_technicals' in analyst_insights:
            tech = analyst_insights['key_technicals']
            f.write("Key Technical Levels:\n")
            f.write(f"  Support: ${tech['support']}\n")
            f.write(f"  Resistance: ${tech['resistance']}\n")
            f.write(f"  Stop Loss: ${tech['stop_loss']}\n\n")
        
        if 'valuation' in analyst_insights:
            val = analyst_insights['valuation']
            f.write("Valuation Assessment:\n")
            f.write(f"  {val['description']}\n")
            f.write(f"  Discount: {val['discount']}\n")
            f.write(f"  Relative Value: {val['relative_value']}\n\n")
        
        if 'company_metrics' in analyst_insights:
            metrics = analyst_insights['company_metrics']
            f.write("Company Metrics (scale 1-10):\n")
            f.write(f"  Innovativeness: {metrics['innovativeness']}\n")
            f.write(f"  Hiring: {metrics['hiring']}\n")
            f.write(f"  Sustainability: {metrics['sustainability']}\n")
            f.write(f"  Insider Sentiments: {metrics['insider_sentiments']}\n")
            f.write(f"  Earnings Reports: {metrics['earnings_reports']}\n\n")
        
        if 'significant_developments' in analyst_insights:
            f.write("Recent Significant Developments:\n")
            for dev in analyst_insights['significant_developments'][:5]:  # Show top 5
                f.write(f"  {dev['date']}: {dev['headline']}\n")
            f.write("\n")
    else:
        f.write("No analyst insights data available.\n\n")
    
    # Analyst Reports
    f.write("RECENT ANALYST REPORTS\n")
    f.write("---------------------\n")
    if analyst_reports:
        for i, report in enumerate(analyst_reports[:5], 1):  # Show top 5
            f.write(f"{i}. {report['title']}\n")
            f.write(f"   Provider: {report['provider']}\n")
            f.write(f"   Author: {report['author']}\n")
            f.write(f"   Date: {report['date']}\n")
            f.write(f"   Summary: {report['abstract'][:200]}...\n\n")
    else:
        f.write("No recent analyst reports available.\n\n")
    
    # Insider Trading
    f.write("INSIDER TRADING ACTIVITY\n")
    f.write("-----------------------\n")
    if insider_trades:
        for i, trade in enumerate(insider_trades[:5], 1):  # Show top 5
            f.write(f"{i}. {trade['name']} ({trade['relation']})\n")
            f.write(f"   Transaction: {trade['transaction']}\n")
            f.write(f"   Date: {trade['date']}\n")
            f<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>