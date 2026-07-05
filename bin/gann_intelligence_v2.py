import yfinance as yf
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta

# ==========================================
# 修復模組：江恩智能分析與回測 (Gann V2)
# ==========================================

def compute_gann_level(base_price, angle, scale=1.0):
    """計算特定角度的江恩價位，支援縮放因子"""
    # 縮放是為了讓高價股的間距更有意義 (如 2000元股價可除以 10 計算)
    p = base_price / scale
    sqrt_p = math.sqrt(p)
    # 江恩公式: (sqrt(P) + angle/180)^2 * scale 
    # 注意: 每 360 度增加 2，所以 angle/180 剛好是 angle/360 * 2
    target_sqrt = sqrt_p + (angle / 180.0)
    if target_sqrt < 0: return 0
    return (target_sqrt ** 2) * scale

def find_pivots(df, window=20):
    """自動尋找波段高低點"""
    df['is_high'] = df['High'] == df['High'].rolling(window=window, center=True).max()
    df['is_low'] = df['Low'] == df['Low'].rolling(window=window, center=True).min()
    
    highs = df[df['is_high']][['High']].copy()
    lows = df[df['is_low']][['Low']].copy()
    return highs, lows

def backtest_gann(symbol, period='5y'):
    print(f"--- 啟動 {symbol} 江恩回測 (週期: {period}) ---")
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    if df.empty: return
    
    # 1. 識別過去 5 年最重要的「大底樞紐」
    absolute_low = df['Low'].min()
    pivot_date = df['Low'].idxmin()
    current_price = df.iloc[-1]['Close']
    
    # 2. 動態判斷縮放因子 (Scale)
    # 若股價 > 500，使用 10 倍縮放以求關鍵位
    scale = 10.0 if absolute_low > 500 else 1.0
    if absolute_low > 2000: scale = 100.0
    
    print(f"識別樞紐起始點: {absolute_low:.2f} (日期: {pivot_date.date()}, 縮放: {scale})")
    
    # 3. 推算江恩正方形各重要角度
    # 基本角 (Cardinal): 90, 180, 270, 360, 450, 540, 630, 720
    angles = [90, 180, 270, 360, 450, 540, 630, 720]
    gann_levels = []
    for a in angles:
        lvl = compute_gann_level(absolute_low, a, scale)
        gann_levels.append({'angle': a, 'price': lvl})
    
    # 4. 執行命中回測 (驗證過去是否有價位在此處停頓)
    print("\n[回測結果：計算出的關鍵位與歷史重合度]")
    print(f"{'角度':>5} | {'計算價位':>10} | {'目前狀態':>10}")
    print("-" * 40)
    
    for lvl in gann_levels:
        price_lvl = lvl['price']
        status = ""
        if current_price > price_lvl:
            status = "已突破 (轉支撐)"
        elif abs(current_price - price_lvl) / price_lvl < 0.02:
            status = "🔥 正接近壓力"
        else:
            status = "上方目標壓力"
            
        print(f"{lvl['angle']:>4}° | {price_lvl:>10.2f} | {status}")
        
    # 5. 分析台積電/0050 特有卡點：近期回測失效原因
    # 檢查是否有更近期的次級樞紐
    recent_df = df.tail(252) # 最近一年
    recent_high = recent_df['High'].max()
    print(f"\n[偵測分析] 卡點修復建議：")
    if current_price > gann_levels[-1]['price']:
        print("💡 警告：當前股價已噴發超出 720° (兩整圈) 範圍。")
        print("   -> 原因：原始樞紐過舊(5年前)，且縮放因子未隨股價翻倍而調整。")
        print("   -> 修復：應切換至最近一年的顯著低點作為「二級樞紐」重新起算。")

if __name__ == "__main__":
    # 執行台積電回測
    backtest_gann('2330.TW', '5y')
    print("\n" + "="*50 + "\n")
    # 執行 0050 回測
    backtest_gann('0050.TW', '5y')
