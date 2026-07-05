import json
import os
import time
from datetime import datetime, timedelta, timezone
from google import genai
from google.genai import types
import yfinance as yf
from dateutil import parser

# ==========================================
# 模組二：AI 分析與量化動能計算 (Analysis)
# ==========================================

CONFIG_PATH = "brain/config.json"
SKILLS_PATH = "skills/kol_analyst.md"
INPUT_PATH = "drafts/raw_episodes.json"
OUTPUT_PATH = "drafts/ai_analysis.json"

TODAY = datetime.now(timezone.utc)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_with_gemini(client, text_content, skill_prompt):
    print("[2/4] Calling Gemini AI for macro synthesis...")
    full_prompt = f"{skill_prompt}\n\nHere is the podcast notes content to analyze:\n{text_content}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        data = json.loads(response.text)
        if isinstance(data, list):
            data = data[0] if len(data) > 0 else {}
        return data
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {}

def is_mentioned(stock, text):
    ticker_base = stock.get('ticker', '').split('.')[0]
    name = stock.get('name', '')
    text_lower = text.lower()
    if ticker_base and ticker_base.lower() in text_lower: return True
    if name and len(name) >= 2 and name.lower() in text_lower: return True
    return False

def calculate_stock_performance(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty: return None
        closes = hist['Close'].tolist()
        start_price = closes[0]
        end_price = closes[-1]
        if start_price == 0: return None
        pct_change = ((end_price - start_price) / start_price) * 100
        # 這裡只儲存純價格資料，畫圖的邏輯留給 Render 模組
        return {
            'end_price': end_price,
            'pct_change': pct_change,
            'price_history': closes
        }
    except Exception:
        return None

def main():
    if not os.environ.get("GEMINI_API_KEY"):
         print("❌ Error: GEMINI_API_KEY is not set.")
         return

    config = load_json(CONFIG_PATH)
    all_episodes = load_json(INPUT_PATH)
    
    with open(SKILLS_PATH, 'r', encoding='utf-8') as f:
        skill_prompt = f.read()

    # 日期過濾
    recent_days = config["scraping"]["analysis_recent_days"]
    threshold_date = TODAY - timedelta(days=recent_days)
    recent_episodes = [ep for ep in all_episodes if parser.parse(ep['published']) >= threshold_date]
    if not recent_episodes and all_episodes: recent_episodes = [all_episodes[0]]

    combined_text = "\n\n".join([f"Title: {ep['title']}\nContent:\n{ep['summary']}" for ep in recent_episodes])
    
    client = genai.Client()
    analysis = analyze_with_gemini(client, combined_text, skill_prompt)
    
    stock_results = []
    seen_tickers = set()
    
    print("[2/4] Calculating rolling counts & fetching market data...")
    for stock in analysis.get('extracted_stocks', []):
        ticker = stock.get('ticker')
        if not ticker or ticker in seen_tickers: continue
        seen_tickers.add(ticker)
        
        count_1m = count_3m = count_6m = 0
        for ep in all_episodes:
            ep_date = parser.parse(ep['published'])
            if is_mentioned(stock, ep['summary']):
                if ep_date >= TODAY - timedelta(days=30): count_1m += 1
                if ep_date >= TODAY - timedelta(days=90): count_3m += 1
                if ep_date >= TODAY - timedelta(days=180): count_6m += 1
                
        perf = calculate_stock_performance(ticker)
        
        stock_results.append({
            'ticker': ticker, 'name': stock.get('name', ''),
            'sentiment': stock.get('sentiment', 0), 'reason': stock.get('reason', ''),
            'performance': perf, 'counts': {'1m': count_1m, '3m': count_3m, '6m': count_6m}
        })
        time.sleep(0.2)
        
    final_output = {
        'macro_summary': analysis.get('macro_summary', ''),
        'investment_direction': analysis.get('investment_direction', ''),
        'core_perspective': analysis.get('core_perspective', ''),
        'stocks': stock_results
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    print(f"[2/4] Success! Saved AI analysis to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()