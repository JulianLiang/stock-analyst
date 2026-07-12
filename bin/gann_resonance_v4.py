import yfinance as yf
import pandas as pd
import math
import numpy as np
from datetime import datetime, timedelta

# ===================================================
# 江恩共振回測 V4：價格與時間的時空交會 (Gann Resonance)
# ===================================================

def get_gann_price_levels(base_price, rings=5):
    """計算江恩正方形 (Square of 9) 基本角位階"""
    levels = []
    sqrt_p = math.sqrt(base_price)
    # 往外算 N 圈的所有 45 度角
    for angle in range(45, 360 * rings + 1, 45):
        target_sqrt = sqrt_p + (angle / 180.0)
        levels.append({'angle': angle, 'price': target_sqrt ** 2})
    return levels

def get_gann_time_cycles(base_date, max_days=1800):
    """計算江恩時間週期 (基於 360 度旋轉，1度 ≈ 1天)"""
    cycles = []
    # 江恩重要的時間轉折角度: 90, 180, 270, 360, 450...
    for angle in range(90, max_days + 1, 90):
        target_date = base_date + timedelta(days=angle)
        cycles.append({'angle': angle, 'date': target_date})
    return cycles

def find_actual_pivots(df, order=15):
    """識別實質波段轉折點"""
    pivots = []
    for i in range(order, len(df) - order):
        is_low = df['Low'].iloc[i] == df['Low'].iloc[i-order:i+order+1].min()
        is_high = df['High'].iloc[i] == df['High'].iloc[i-order:i+order+1].max()
        if is_low:
            pivots.append({'date': df.index[i], 'price': df['Low'].iloc[i], 'type': 'Low'})
        elif is_high:
            pivots.append({'date': df.index[i], 'price': df['High'].iloc[i], 'type': 'High'})
    return pivots

def run_resonance_backtest(symbol='0050.TW'):
    print(f"🚀 啟動 {symbol} 江恩時空共振 (Resonance) 深度回測...")
    stock = yf.Ticker(symbol)
    df = stock.history(period="5y", auto_adjust=True)
    if df.empty: return

    # 1. 找出「大底樞紐」作為宇宙中心 (0,0)
    master_low = df['Low'].min()
    master_pivot_date = df['Low'].idxmin()
    print(f"宇宙起點 (Master Pivot): {master_low:.2f} ({master_pivot_date.date()})\n")

    # 2. 預測網格：算出未來所有的江恩價位與時間點
    pred_prices = get_gann_price_levels(master_low, rings=10)
    pred_times = get_gann_time_cycles(master_pivot_date)

    # 3. 實戰驗證：找出歷史轉折點
    actual_pivots = find_actual_pivots(df)
    
    resonance_hits = 0
    total_pivots = len(actual_pivots)
    
    print(f"{'轉折日期':<12} | {'類型':<4} | {'實際價':>6} | {'價格誤差':>6} | {'時間誤差':>5} | 判定")
    print("-" * 75)

    for p in actual_pivots:
        # A. 找尋最近的江恩價格
        min_p_err = 999.0
        for lp in pred_prices:
            err = abs(p['price'] - lp['price']) / lp['price']
            if err < min_p_err: min_p_err = err
        
        # B. 找尋最近的江恩時間
        min_t_err = 999
        for lt in pred_times:
            err = abs((p['date'] - lt['date']).days)
            if err < min_t_err: min_t_err = err
            
        # 判定：時空共振 (Resonance)
        # 門檻：價格誤差 < 2.5%, 時間誤差 < 7 天 (一週)
        is_price_hit = min_p_err < 0.025
        is_time_hit = min_t_err <= 7
        
        label = ""
        if is_price_hit and is_time_hit:
            resonance_hits += 1
            label = "🔥 時空共振 (RESONANCE)!"
        elif is_price_hit:
            label = "📐 僅價格命中"
        elif is_time_hit:
            label = "⏳ 僅時間命中"

        print(f"{str(p['date'].date()):<12} | {p['type']:<4} | {p['price']:>7.2f} | {min_p_err*100:>6.1f}% | {min_t_err:>3}天 | {label}")

    # 4. 總結報告
    hit_rate = (resonance_hits / total_pivots) * 100 if total_pivots > 0 else 0
    print("-" * 75)
    print(f"📊 最終共振報告 (Resonance Report):")
    print(f"   - 總轉折點數: {total_pivots}")
    print(f"   - 時空共振點 (Price+Time): {resonance_hits}")
    print(f"   - 強共振命中率: {hit_rate:.2f}%")
    
    print("\n💡 專業解讀：")
    print("   江恩認為『時間』重於『價格』。當你發現一個轉折點『僅價格命中』時，它通常只是小波段；")
    print("   只有當『時間與價格同時到位』，才會爆發如 2024/07 或 2022/10 那樣的大級別行情。")

if __name__ == "__main__":
    run_resonance_backtest()
