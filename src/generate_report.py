import yfinance as yf
from google import genai
from google.genai import types
import json
import os
import re
from datetime import datetime, timedelta, timezone
from dateutil import parser
import requests
import time
import concurrent.futures
import urllib.parse

# --- Configurations ---
SKILLS_PATH = "skills/kol_analyst.md"
REPORT_PATH = "report.html"
MAX_EPISODES = 50  # 擴大抓取量以涵蓋 6 個月的歷史資料
INDEX_URL = "https://whatmkreallysaid.com/episodes.json"

# Mock today's date based on context (July 4, 2026)
TODAY = datetime(2026, 7, 4, tzinfo=timezone.utc)
ONE_MONTH_AGO = TODAY - timedelta(days=30)
THREE_MONTHS_AGO = TODAY - timedelta(days=90)
SIX_MONTHS_AGO = TODAY - timedelta(days=180)

def clean_transcript(text):
    if not text:
        return ""
    
    # 1. 強化版：精準切除「贊助」區塊
    text = re.sub(r'##\s*贊助.*?(?=##|$)', '', text, flags=re.DOTALL)
    
    # 2. 移除連結
    text = re.sub(r'https?://\S+', '', text)
    
    # 3. 移除常見廣告關鍵字
    ad_pattern = re.compile(
        r'.*(折扣碼|優惠碼|NordVPN|植村秀|東璧堂|蝦皮|團購|輸入碼|官方網站|點擊連結|結帳輸入|專屬優惠|本集節目由).*',
        re.IGNORECASE | re.MULTILINE
    )
    cleaned_text = re.sub(ad_pattern, '', text)
    
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.replace("發哥", "聯發科(2454.TW)")
    
    return cleaned_text.strip()

def fetch_notes_metadata():
    print(f"Fetching index from: {INDEX_URL}")
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        response = requests.get(INDEX_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        data.sort(key=lambda x: x.get('number', 0), reverse=True)
        return data[:MAX_EPISODES]
    except Exception as e:
        print(f"Error fetching index: {e}")
        return []

def extract_content_from_note(ep_meta):
    filename = ep_meta.get('filename')
    if not filename:
        return None
        
    url = f"https://whatmkreallysaid.com/episodes/{urllib.parse.quote(filename)}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        title = ep_meta.get('title', 'Unknown Title')
        pub_date_str = ep_meta.get('date')
        if pub_date_str:
            pub_date = parser.parse(pub_date_str).astimezone(timezone.utc)
        else:
            pub_date = TODAY
            
        raw_md = response.text
        cleaned_text = clean_transcript(raw_md)
        
        # 解除截斷鎖定，確保不漏掉節目後半段點名的股票
        return {'title': title, 'published': pub_date, 'summary': cleaned_text}
    except Exception as e:
        print(f"Error extracting {filename}: {e}")
        return None

def fetch_all_episodes():
    ep_metadata = fetch_notes_metadata()
    episodes = []
    print(f"Parallel extracting {len(ep_metadata)} episodes...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_content_from_note, meta) for meta in ep_metadata]
        for future in concurrent.futures.as_completed(futures):
            ep_data = future.result()
            if ep_data and len(ep_data['summary']) > 50:
                episodes.append(ep_data)
    episodes.sort(key=lambda x: x['published'], reverse=True)
    return episodes

def read_skill_prompt():
    with open(SKILLS_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def analyze_with_gemini(client, text_content, skill_prompt):
    print("Analyzing hardcore notes with Gemini...")
    full_prompt = f"{skill_prompt}\n\nHere is the podcast notes content to analyze:\n{text_content}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"macro_summary": "", "investment_direction": "", "core_perspective": "", "extracted_stocks": []}

def generate_sparkline_svg(prices, width=120, height=40):
    if not prices or len(prices) < 2:
        return ""
    
    min_p, max_p = min(prices), max(prices)
    range_p = max_p - min_p if max_p != min_p else 1
    
    # Calculate coordinates
    pts = []
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * width
        y = height - ((p - min_p) / range_p) * height
        pts.append(f"{x},{y}")
        
    path_data = " ".join(pts)
    
    # Determine color (green for up, red for down)
    color = "#059669" if prices[-1] >= prices[0] else "#dc2626"
    
    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 -5 {width} {height+10}" fill="none" xmlns="http://www.w3.org/2000/svg">
        <polyline points="{path_data}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="{pts[-1].split(',')[0]}" cy="{pts[-1].split(',')[1]}" r="3" fill="{color}"/>
    </svg>
    """
    return svg

def calculate_stock_performance(ticker):
    print(f"Fetching 1M trend for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        # 抓取最近 1 個月的歷史資料
        hist = stock.history(period="1mo")
        if hist.empty: return None
            
        closes = hist['Close'].tolist()
        start_price = closes[0]
        end_price = closes[-1]
        
        if start_price == 0: return None
             
        pct_change = ((end_price - start_price) / start_price) * 100
        svg_chart = generate_sparkline_svg(closes)
        
        return {
            'end_price': end_price,
            'pct_change': pct_change,
            'svg_chart': svg_chart
        }
    except Exception:
        return None

def is_mentioned(stock, text):
    ticker_base = stock.get('ticker', '').split('.')[0]
    name = stock.get('name', '')
    text_lower = text.lower()
    
    if ticker_base and ticker_base.lower() in text_lower:
        return True
    if name and len(name) >= 2 and name.lower() in text_lower:
        return True
    return False

def process_episodes(client, all_episodes, skill_prompt):
    if not all_episodes: return {"macro_summary": "", "investment_direction": "", "stocks": []}
        
    recent_episodes = all_episodes[:5]
    print(f"\nProcessing {len(recent_episodes)} recent episodes with AI...")
    combined_text = "\n\n".join([f"Title: {ep['title']}\nDate: {ep['published'].strftime('%Y-%m-%d')}\nContent:\n{ep['summary']}" for ep in recent_episodes])
    
    analysis = analyze_with_gemini(client, combined_text, skill_prompt)
    
    # 確保 analysis 是一個 dict。如果 AI 誤回傳 list，取第一個元素
    if isinstance(analysis, list):
        if len(analysis) > 0:
            analysis = analysis[0]
        else:
            analysis = {"macro_summary": "", "investment_direction": "", "core_perspective": "", "extracted_stocks": []}
            
    stock_results = []
    seen_tickers = set()
    
    print("Calculating rolling counts and generating trendlines...")
    for stock in analysis.get('extracted_stocks', []):
        ticker = stock.get('ticker')
        if not ticker or ticker in seen_tickers: continue
        seen_tickers.add(ticker)
        
        count_1m = count_3m = count_6m = 0
        for ep in all_episodes:
            if is_mentioned(stock, ep['summary']):
                if ep['published'] >= ONE_MONTH_AGO: count_1m += 1
                if ep['published'] >= THREE_MONTHS_AGO: count_3m += 1
                if ep['published'] >= SIX_MONTHS_AGO: count_6m += 1
                
        # 改為抓取近一個月趨勢
        perf = calculate_stock_performance(ticker)
        
        stock_results.append({
            'ticker': ticker, 
            'name': stock.get('name', ''),
            'sentiment': stock.get('sentiment', 0), 
            'reason': stock.get('reason', ''),
            'performance': perf,
            'counts': {'1m': count_1m, '3m': count_3m, '6m': count_6m}
        })
        time.sleep(0.5)
        
    return {
        'macro_summary': analysis.get('macro_summary', ''),
        'investment_direction': analysis.get('investment_direction', ''),
        'core_perspective': analysis.get('core_perspective', ''),
        'stocks': stock_results
    }

def generate_html_report(result):
    print("\nGenerating HTML report...")
    
    html = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>股癌 Podcast 專業投資組合與趨勢研報</title>
        <style>
            :root {
                --primary: #1e3a8a;
                --secondary: #3b82f6;
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #0f172a;
                --text-light: #475569;
                --positive: #059669;
                --negative: #dc2626;
                --neutral: #d97706;
                --border: #cbd5e1;
            }
            body { font-family: 'Helvetica Neue', Arial, 'LiHei Pro', 'Microsoft JhengHei', sans-serif; background-color: var(--bg); color: var(--text); line-height: 1.8; margin: 0; padding: 2rem; }
            .container { max-width: 1400px; margin: 0 auto; }
            .header-section { text-align: center; margin-bottom: 3rem; padding: 3rem 2rem; background: linear-gradient(135deg, #0f172a, #1e293b); color: white; border-radius: 20px; box-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.1); }
            h1 { margin: 0 0 1rem 0; font-size: 2.8rem; letter-spacing: 2px; }
            .section { background: var(--card-bg); border-radius: 20px; padding: 2.5rem; margin-bottom: 3rem; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05); }
            .section-title { border-bottom: 3px solid var(--primary); padding-bottom: 0.75rem; margin-top: 0; margin-bottom: 1.5rem; color: var(--text); font-size: 1.75rem; font-weight: 700; }
            .content-box { background-color: #f1f5f9; border-left: 6px solid var(--primary); padding: 2rem; margin-bottom: 2rem; border-radius: 0 12px 12px 0; text-align: justify; }
            .content-box.strategy { border-left-color: var(--neutral); background-color: #fffbeb; }
            .content-box h4 { margin-top: 0; color: var(--primary); font-size: 1.35rem; margin-bottom: 1rem; }
            .content-box.strategy h4 { color: var(--neutral); }
            .content-box.perspective { border-left-color: var(--secondary); background-color: #eff6ff; }
            .content-box.perspective h4 { color: var(--secondary); }
            .content-box p { margin: 0; font-size: 1.1rem; color: var(--text-light); white-space: pre-wrap; }
            table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 1.5rem; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
            th, td { padding: 1.25rem 1rem; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle;}
            th { background-color: #f8fafc; font-weight: 700; color: var(--text); font-size: 1.05rem; }
            tr:last-child td { border-bottom: none; }
            tr:hover { background-color: #f1f5f9; }
            .sentiment-1 { color: var(--positive); font-weight: bold; background: #d1fae5; padding: 6px 10px; border-radius: 6px; }
            .sentiment-0 { color: var(--neutral); font-weight: bold; background: #fef3c7; padding: 6px 10px; border-radius: 6px; }
            .sentiment--1 { color: var(--negative); font-weight: bold; background: #fee2e2; padding: 6px 10px; border-radius: 6px; }
            .reason-cell { max-width: 320px; line-height: 1.6; color: var(--text-light); font-size: 0.95rem; }
            .ticker { font-size: 1.2rem; color: var(--primary); letter-spacing: 0.5px; }
            .table-title { margin-top: 2rem; font-size: 1.4rem; color: var(--text); }
            
            .badge-container { display: flex; gap: 6px; flex-wrap: wrap; }
            .badge { display: inline-flex; align-items: center; justify-content: center; padding: 4px 8px; border-radius: 6px; font-size: 0.85rem; font-weight: 700; }
            .badge-1m { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
            .badge-3m { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
            .badge-6m { background-color: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
            .badge span { margin-right: 4px; opacity: 0.8; font-size: 0.75rem; font-weight: normal; }
            
            /* Trend chart styles */
            .trend-cell { min-width: 130px; }
            .price-block { display: flex; flex-direction: column; align-items: flex-end; }
            .price-val { font-size: 1.15rem; font-weight: 700; color: var(--text); }
            .price-change { font-size: 0.9rem; font-weight: 600; }
            .price-change.up { color: var(--positive); }
            .price-change.down { color: var(--negative); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>股癌 Podcast 專業投資組合與趨勢研報</h1>
                <p style="color: #94a3b8; font-size: 1.2rem; margin-bottom: 0.5rem;">AI 自動化深度解析與歷史回測報告</p>
                <p style="color: #64748b; font-size: 0.95rem;">資料來源：whatmkreallysaid.com ｜ 涵蓋過去 6 個月資料</p>
                <p style="color: #64748b; font-size: 0.95rem;">報告產生時間: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">最新深度筆記分析</h2>
    """
    
    if result['macro_summary']:
        html += f'<div class="content-box"><h4>📉 宏觀經濟與產業趨勢總結</h4><p>{result["macro_summary"]}</p></div>'
        
    if result['investment_direction']:
        html += f'<div class="content-box strategy"><h4>🎯 投資方向與策略</h4><p>{result["investment_direction"]}</p></div>'
        
    if result.get('core_perspective'):
        html += f'<div class="content-box perspective"><h4>💡 核心投資觀點 (QA 心法)</h4><p>{result["core_perspective"]}</p></div>'
        
    html += '<h3 class="table-title">📊 提及與關聯標的動能追蹤</h3>'
    if result['stocks']:
        html += """
        <table>
            <thead>
                <tr>
                    <th>標的代碼</th>
                    <th>名稱</th>
                    <th>AI 情緒</th>
                    <th>🔥 滾動提及頻次<br><small style="font-weight: normal; color: var(--text-light);">(1M / 3M / 6M)</small></th>
                    <th>點名或關聯原因摘要</th>
                    <th>📈 近 1M 趨勢圖</th>
                    <th style="text-align: right;">現價與月漲跌</th>
                </tr>
            </thead>
            <tbody>
        """
        for stock in result['stocks']:
            sentiment_map = {1: "看多/受惠", 0: "中性/觀察", -1: "看空/避開"}
            sentiment_class = f"sentiment-{stock['sentiment']}"
            sentiment_text = sentiment_map.get(stock['sentiment'], "未知")
            
            perf = stock['performance']
            if perf:
                change_class = "up" if perf['pct_change'] >= 0 else "down"
                change_sign = "+" if perf['pct_change'] >= 0 else ""
                
                price_html = f"""
                <div class="price-block">
                    <span class="price-val">{perf['end_price']:.2f}</span>
                    <span class="price-change {change_class}">{change_sign}{perf['pct_change']:.2f}%</span>
                </div>
                """
                svg_html = perf['svg_chart']
            else:
                price_html = "<span style='color: #94a3b8;'>無報價</span>"
                svg_html = "-"
                
            counts = stock.get('counts', {'1m': 0, '3m': 0, '6m': 0})
            badges_html = f"""
                <div class="badge-container">
                    <div class="badge badge-1m"><span>1M</span>{counts['1m']} 次</div>
                    <div class="badge badge-3m"><span>3M</span>{counts['3m']} 次</div>
                    <div class="badge badge-6m"><span>6M</span>{counts['6m']} 次</div>
                </div>
            """
            
            html += f"""
                <tr>
                    <td><strong class="ticker">{stock['ticker']}</strong></td>
                    <td style="font-weight: 500;">{stock['name']}</td>
                    <td><span class="{sentiment_class}">{sentiment_text}</span></td>
                    <td>{badges_html}</td>
                    <td class="reason-cell">{stock['reason']}</td>
                    <td class="trend-cell">{svg_html}</td>
                    <td>{price_html}</td>
                </tr>
            """
        html += "</tbody></table>"
    else:
         html += '<p style="color: var(--text-light); padding: 1.5rem; background: #f8fafc; border-radius: 8px; border: 1px dashed var(--border);">在此期間無提取出具體的股票標的。</p>'
         
    html += """
        </div>
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
    episodes = fetch_all_episodes()
    
    result = process_episodes(client, episodes, skill_prompt)
    generate_html_report(result)

if __name__ == "__main__":
    main()
