import yfinance as yf
import pandas as pd
import math
import json
import os
from datetime import datetime, timezone

# ==========================================
# 修復模組：江恩智能分析 (Gann V3) - 整合版
# ==========================================

OUTPUT_PATH = "drafts/gann_analysis.json"

def compute_gann_price(base, angle, scale=1.0):
    return (math.sqrt(base/scale) + (angle/180.0))**2 * scale

def analyze_stock(symbol, name):
    print(f"Analyzing Gann levels for {name} ({symbol})...")
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="5y")
        if df.empty: return None

        curr_price = df.iloc[-1]['Close']
        p1_price = df['Low'].min()
        p1_date = df['Low'].idxmin().strftime('%Y-%m-%d')
        
        recent_df = df.tail(252)
        p2_price = recent_df['Low'].min()
        p2_date = recent_df['Low'].idxmin().strftime('%Y-%m-%d')
        
        scale = 10.0 if curr_price > 1000 else 1.0
        
        levels = []
        angle = 90
        while True:
            p = compute_gann_price(p2_price, angle, scale)
            
            status = "unknown"
            if abs(curr_price - p) / p < 0.015:
                status = "pivot" # 關鍵位
            elif p < curr_price:
                status = "support"
            else:
                status = "resistance"

            levels.append({
                "angle": angle,
                "price": round(p, 2),
                "status": status
            })
            
            if p > curr_price * 1.25: break
            angle += 45
            if angle > 3600: break

        return {
            "symbol": symbol,
            "name": name,
            "current_price": round(curr_price, 2),
            "pivots": {
                "primary": {"price": round(p1_price, 2), "date": p1_date},
                "secondary": {"price": round(p2_price, 2), "date": p2_date}
            },
            "levels": levels[-8:] # 只取最靠近現價的 8 個位階
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def main():
    # 這裡預設分析 2330 和 0050，未來可擴充至 config 讀取
    targets = [
        {"symbol": "2330.TW", "name": "台積電"},
        {"symbol": "0050.TW", "name": "元大台灣50"}
    ]
    
    results = []
    for t in targets:
        res = analyze_stock(t["symbol"], t["name"])
        if res:
            results.append(res)
            
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Gann analysis results saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
