import feedparser
import yfinance as yf
from google import genai
from google.genai import types
import json
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import requests
from collections import defaultdict
import time

# --- Configurations ---
SKILLS_PATH = "skills/kol_analyst.md"
REPORT_PATH = "report.html"
MAX_EPISODES_PER_GROUP = 5

# Mock today's date based on context (July 4, 2026)
TODAY = datetime(2026, 7, 4, tzinfo=timezone.utc)
ONE_MONTH_AGO = TODAY - timedelta(days=30)
THREE_MONTHS_AGO = TODAY - timedelta(days=90)
SIX_MONTHS_AGO = TODAY - timedelta(days=180)

def get_apple_podcast_rss():
    print("Searching Apple Podcast API for 股癌...")
    search_url = "https://itunes.apple.com/search?term=股癌&entity=podcast&country=tw"
    try:
        response = requests.get(search_url)
        data = response.json()
        if data.get("resultCount", 0) > 0:
            feed_url = data["results"][0].get("feedUrl")
            print(f"Found feed URL: {feed_url}")
            return feed_url
        else:
            print("Could not find podcast on Apple API.")
            return None
    except Exception as e:
        print(f"Error fetching from Apple API: {e}")
        return None

def fetch_and_group_episodes():
    rss_url = get_apple_podcast_rss()
    if not rss_url:
        return {'1_month': [], '3_months': [], '6_months': []}
        
    print(f"Fetching RSS feed from {rss_url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    response = requests.get(rss_url, headers=headers)
    feed = feedparser.parse(response.content)
    
    episodes = {
        '1_month': [],
        '3_months': [],
        '6_months': []
    }
    
    for entry in feed.entries:
        try:
            pub_date = parsedate_to_datetime(entry.published).astimezone(timezone.utc)
        except Exception as e:
            print(f"Error parsing date {entry.get('published')}: {e}")
            continue
            
        episode_data = {
            'title': entry.title,
            'published': pub_date,
            'summary': entry.summary
        }
        
        # Determine group
        if pub_date >= ONE_MONTH_AGO and pub_date <= TODAY:
            if len(episodes['1_month']) < MAX_EPISODES_PER_GROUP:
                episodes['1_month'].append(episode_data)
        elif pub_date >= THREE_MONTHS_AGO and pub_date < ONE_MONTH_AGO:
            if len(episodes['3_months']) < MAX_EPISODES_PER_GROUP:
                episodes['3_months'].append(episode_data)
        elif pub_date >= SIX_MONTHS_AGO and pub_date < THREE_MONTHS_AGO:
            if len(episodes['6_months']) < MAX_EPISODES_PER_GROUP:
                episodes['6_months'].append(episode_data)
                
    return episodes

def read_skill_prompt():
    with open(SKILLS_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def analyze_with_gemini(client, text_content, skill_prompt):
    print("Analyzing content with Gemini...")
    full_prompt = f"{skill_prompt}\n\nHere is the podcast content to analyze:\n{text_content}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from response: {e}")
            print(f"Raw response: {response.text}")
            return {"macro_themes": [], "extracted_stocks": []}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"macro_themes": [], "extracted_stocks": []}

def calculate_stock_performance(ticker, start_date):
    print(f"Fetching data for {ticker} starting {start_date.strftime('%Y-%m-%d')}...")
    end_date = start_date + timedelta(days=180)
    
    if end_date > TODAY:
        end_date = TODAY
        
    start_date_str = start_date.strftime('%Y-%m-%d')
    # Add a few days buffer to end date to ensure we get a quote
    end_date_str = (end_date + timedelta(days=3)).strftime('%Y-%m-%d')
    
    try:
        stock = yf.Ticker(ticker)
        # Suppress yfinance output to keep console clean
        hist = stock.history(start=start_date_str, end=end_date_str)
        
        if hist.empty:
            return None
            
        start_price = hist.iloc[0]['Close']
        end_price = hist.iloc[-1]['Close']
        
        if start_price == 0:
             return None
             
        pct_change = ((end_price - start_price) / start_price) * 100
        
        return {
            'start_price': start_price,
            'end_price': end_price,
            'pct_change': pct_change,
            'is_6_months': end_date == start_date + timedelta(days=180)
        }
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def process_group(client, group_name, episodes, skill_prompt):
    if not episodes:
        return {"themes": [], "stocks": []}
        
    print(f"\nProcessing group: {group_name} ({len(episodes)} episodes)")
    combined_text = "\n\n".join([f"Title: {ep['title']}\nDate: {ep['published'].strftime('%Y-%m-%d')}\nSummary: {ep['summary']}" for ep in episodes])
    
    analysis = analyze_with_gemini(client, combined_text, skill_prompt)
    
    stock_results = []
    # Deduplicate stocks within the group by ticker
    seen_tickers = set()
    
    for stock in analysis.get('extracted_stocks', []):
        ticker = stock.get('ticker')
        if not ticker or ticker in seen_tickers:
            continue
            
        seen_tickers.add(ticker)
        # Use the date of the most recent episode in the group as a proxy for the 'mention date'
        # Or better, just use the first episode's date in this group that we combined
        mention_date = episodes[0]['published'] 
        
        perf = calculate_stock_performance(ticker, mention_date)
        
        stock_results.append({
            'ticker': ticker,
            'name': stock.get('name', ''),
            'sentiment': stock.get('sentiment', 0),
            'reason': stock.get('reason', ''),
            'performance': perf
        })
        time.sleep(1) # Rate limiting for yfinance
        
    return {
        'themes': analysis.get('macro_themes', []),
        'stocks': stock_results
    }

def generate_html_report(results):
    print("\nGenerating HTML report...")
    
    html = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>股癌 Podcast 投資情緒與標的分析報告</title>
        <style>
            :root {
                --primary: #2563eb;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #1e293b;
                --text-light: #64748b;
                --positive: #10b981;
                --negative: #ef4444;
                --neutral: #f59e0b;
                --border: #e2e8f0;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg);
                color: var(--text);
                line-height: 1.6;
                margin: 0;
                padding: 2rem;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                color: var(--primary);
                margin-bottom: 2rem;
            }
            .section {
                background: var(--card-bg);
                border-radius: 12px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            }
            h2 {
                border-bottom: 2px solid var(--border);
                padding-bottom: 0.5rem;
                margin-top: 0;
                color: var(--text);
            }
            .themes-container {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 1.5rem;
            }
            .theme-tag {
                background-color: #dbeafe;
                color: #1d4ed8;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.875rem;
                font-weight: 500;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
            }
            th, td {
                padding: 1rem;
                text-align: left;
                border-bottom: 1px solid var(--border);
            }
            th {
                background-color: #f1f5f9;
                font-weight: 600;
                color: var(--text-light);
            }
            tr:last-child td {
                border-bottom: none;
            }
            .sentiment-1 { color: var(--positive); font-weight: bold; }
            .sentiment-0 { color: var(--neutral); font-weight: bold; }
            .sentiment--1 { color: var(--negative); font-weight: bold; }
            .perf-positive { color: var(--positive); }
            .perf-negative { color: var(--negative); }
            .reason-cell { max-width: 300px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>股癌 Podcast 投資情緒與標的分析報告</h1>
            <p style="text-align: center; color: var(--text-light);">報告產生日期: 2026年7月4日</p>
    """
    
    sections = [
        ('1_month', '過去 1 個月 (近 30 天)'),
        ('3_months', '過去 3 個月 (31 - 90 天前)'),
        ('6_months', '過去 6 個月 (91 - 180 天前)')
    ]
    
    for key, title in sections:
        data = results[key]
        html += f'<div class="section"><h2>{title}</h2>'
        
        # Themes
        html += '<h3>核心投資方向與總經主題</h3>'
        if data['themes']:
            html += '<div class="themes-container">'
            for theme in data['themes']:
                html += f'<span class="theme-tag">{theme}</span>'
            html += '</div>'
        else:
            html += '<p>無提取出特別主題。</p>'
            
        # Stocks Table
        html += '<h3>提及股票與績效追蹤</h3>'
        if data['stocks']:
            html += """
            <table>
                <thead>
                    <tr>
                        <th>股票代碼</th>
                        <th>名稱</th>
                        <th>情緒</th>
                        <th>點名原因摘要</th>
                        <th>點名日價格</th>
                        <th>期末價格 (6月或至今)</th>
                        <th>漲跌幅</th>
                    </tr>
                </thead>
                <tbody>
            """
            for stock in data['stocks']:
                sentiment_map = {1: "看多", 0: "中性", -1: "看空"}
                sentiment_class = f"sentiment-{stock['sentiment']}"
                sentiment_text = sentiment_map.get(stock['sentiment'], "未知")
                
                perf = stock['performance']
                if perf:
                    perf_class = "perf-positive" if perf['pct_change'] >= 0 else "perf-negative"
                    perf_text = f"<span class='{perf_class}'>{perf['pct_change']:.2f}%</span>"
                    start_price = f"{perf['start_price']:.2f}"
                    end_price = f"{perf['end_price']:.2f}"
                    period_note = "(滿 6 個月)" if perf['is_6_months'] else "(未滿 6 個月)"
                    end_price_str = f"{end_price} <br><small style='color:#94a3b8'>{period_note}</small>"
                else:
                    perf_text = "-"
                    start_price = "-"
                    end_price_str = "-"
                
                html += f"""
                    <tr>
                        <td><strong>{stock['ticker']}</strong></td>
                        <td>{stock['name']}</td>
                        <td class="{sentiment_class}">{sentiment_text}</td>
                        <td class="reason-cell">{stock['reason']}</td>
                        <td>{start_price}</td>
                        <td>{end_price_str}</td>
                        <td>{perf_text}</td>
                    </tr>
                """
            html += "</tbody></table>"
        else:
             html += '<p>無提取出相關股票。</p>'
             
        html += '</div>'
        
    html += """
        </div>
    </body>
    </html>
    """
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Report successfully generated at {REPORT_PATH}")

def main():
    if not os.environ.get("GEMINI_API_KEY"):
         print("Error: GEMINI_API_KEY environment variable is not set.")
         return
         
    client = genai.Client()
    skill_prompt = read_skill_prompt()
    episodes_by_group = fetch_and_group_episodes()
    
    results = {}
    for group_name, episodes in episodes_by_group.items():
        results[group_name] = process_group(client, group_name, episodes, skill_prompt)
        
    generate_html_report(results)

if __name__ == "__main__":
    main()
