import yfinance as yf
import pandas as pd
import math
import numpy as np
from datetime import datetime, timedelta

# ==========================================
# 硬核回測：江恩幾何命中率分析 (Gann Backtester)
# ==========================================

def get_gann_levels(base_price, scale=1.0):
    """算出基本角位階 (90, 180, 270, 360, 450, 540, 630, 720)"""
    levels = []
    sqrt_p = math.sqrt(base_price / scale)
    # 往上與往下各算兩圈
    for angle in [-720, -630, -540, -450, -360, -270, -180, -90, 90, 180, 270, 360, 450, 540, 630, 720]:
        target_sqrt = sqrt_p + (angle / 180.0)
        if target_sqrt > 0:
            levels.append((target_sqrt ** 2) * scale)
    return levels

def find_actual_pivots(df, order=20):
    """找出歷史中實質的局部高低點 (轉折點)"""
    pivots = []
    for i in range(order, len(df) - order):
        # 檢查是否為局部低點
        if df['Low'].iloc[i] == df['Low'].iloc[i-order:i+order+1].min():
            pivots.append({'date': df.index[i], 'price': df['Low'].iloc[i], 'type': 'Low'})
        # 檢查是否為局部高點
        if df['High'].iloc[i] == df['High'].iloc[i-order:i+order+1].max():
            pivots.append({'date': df.index[i], 'price': df['High'].iloc[i], 'type': 'High'})
    return pivots

def run_backtest(symbol='0050.TW'):
    print(f"🚀 啟動 {symbol} 過去五年江恩歷史轉折回測...")
    stock = yf.Ticker(symbol)
    # 使用 auto_adjust=True 確保考慮分割與除息
    df = stock.history(period="5y", auto_adjust=True)
    if df.empty: return

    # 1. 找出所有的實質轉折點
    actual_pivots = find_actual_pivots(df)
    print(f"分析完成：過去五年共偵測到 {len(actual_pivots)} 個重大波段轉折。")
    
    hits = 0
    total_checks = 0
    
    print(f"\n{'日期':<12} | {'轉折類型':<6} | {'實際價格':<8} | {'江恩預測位':<8} | 誤差 %")
    print("-" * 65)

    # 2. 逐一比對轉折點與前一個樞紐點產生的江恩位階
    for i in range(1, len(actual_pivots)):
        prev_pivot = actual_pivots[i-1]
        curr_pivot = actual_pivots[i]
        
        # 以「前一個轉折點」作為江恩基準
        base_price = prev_pivot['price']
        predicted_levels = get_gann_levels(base_price, scale=1.0)
        
        # 檢查當前轉折點是否落在預測位附近 (誤差 1.5% 內)
        matched_level = None
        min_error = 999.0
        
        for lvl in predicted_levels:
            error = abs(curr_pivot['price'] - lvl) / lvl
            if error < min_error:
                min_error = error
                matched_level = lvl
        
        total_checks += 1
        is_hit = min_error < 0.015 # 1.5% 門檻
        if is_hit:
            hits += 1
            hit_mark = "🎯 HIT!"
        else:
            hit_mark = ""

        print(f"{str(curr_pivot['date'].date()):<12} | {curr_pivot['type']:<8} | {curr_pivot['price']:>8.2f} | {matched_level:>8.2f} | {min_error*100:>5.2f}% {hit_mark}")

    hit_rate = (hits / total_checks) * 100 if total_checks > 0 else 0
    print("-" * 65)
    print(f"📊 最終回測報告：")
    print(f"   - 總轉折樣本數: {total_checks}")
    print(f"   - 江恩位階命中數: {hits}")
    print(f"   - 綜合命中率 (±1.5% 誤差): {hit_rate:.2f}%")
    
    if hit_rate > 60:
        print("\n💡 結論：江恩幾何在 0050 身上具備顯著的預測力。")
    else:
        print("\n💡 結論：命中率一般，建議搭配其他指標驗證。")

if __name__ == "__main__":
    run_backtest()
