import yfinance as yf
import pandas as pd
import math
import json
import os
from datetime import datetime, timezone

# =========================================================
# 強烈升級：江恩智能分析 (Gann V3.5) - 加入百分比與加碼建議
# =========================================================

OUTPUT_PATH = "drafts/gann_analysis.json"

def compute_gann_price(base, angle, scale=1.0):
    return (math.sqrt(base/scale) + (angle/180.0))**2 * scale

def calculate_retracements(low, high):
    diff = high - low
    return {
        "12.5% (1/8)": round(high - diff * 0.125, 2),
        "25.0% (2/8)": round(high - diff * 0.25, 2),
        "37.5% (3/8)": round(high - diff * 0.375, 2),
        "50.0% (4/8)": round(high - diff * 0.50, 2)
    }

def analyze_stock(symbol, name):
    print(f"Analyzing Deep Gann for {name} ({symbol})...")
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="5y", auto_adjust=True)
        if df.empty: return None

        curr_price = df.iloc[-1]['Close']
        absolute_high = df['High'].max()
        
        # 邏輯：台積電強制對齊 2025/04 基準點 (766.49)
        if symbol == "2330.TW":
            p2_price = 766.49
            p2_date = "2025-04-09"
        else:
            # 其他標的自動抓取近一年低點
            recent_df = df.tail(252)
            p2_price = recent_df['Low'].min()
            p2_date = recent_df['Low'].idxmin().strftime('%Y-%m-%d')
        
        scale = 10.0 if curr_price > 1000 else 1.0
        
        # 1. 幾何角度推算
        levels = []
        angle = 90
        while True:
            p = compute_gann_price(p2_price, angle, scale)
            status = "pivot" if abs(curr_price - p) / p < 0.015 else ("support" if p < curr_price else "resistance")
            levels.append({"angle": angle, "price": round(p, 2), "status": status})
            if p > curr_price * 1.25: break
            angle += 45
            if angle > 4500: break

        # 2. 百分比回檔推算
        retracements = calculate_retracements(p2_price, absolute_high)
        
        # 3. 加碼點位邏輯 (Gann Pyramiding)
        pyramiding = [
            {"level": "激進加碼", "price": f"{compute_gann_price(p2_price, 3960, 10):.0f}~{compute_gann_price(p2_price, 4005, 10):.0f}", "desc": "站穩 3960° 基本角後追擊"},
            {"level": "穩健加碼", "price": f"{compute_gann_price(p2_price, 3870, 10):.0f}", "desc": "回測 3870° 基本角支撐"},
            {"level": "重倉加碼", "price": f"{retracements['12.5% (1/8)']:.0f}", "desc": "波段 1/8 強勢回檔位"}
        ] if symbol == "2330.TW" else []

        return {
            "symbol": symbol,
            "name": name,
            "current_price": round(curr_price, 2),
            "baseline": {"price": p2_price, "date": p2_date},
            "levels": levels[-8:],
            "retracements": retracements,
            "pyramiding": pyramiding
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def main():
    targets = [{"symbol": "2330.TW", "name": "台積電"}, {"symbol": "0050.TW", "name": "元大台灣50"}]
    results = [analyze_stock(t["symbol"], t["name"]) for t in targets]
    results = [r for r in results if r]
            
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Gann analysis results saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
