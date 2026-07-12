import json
from datetime import datetime
import os

# ==========================================
# 模組三：AI Berkshire 品牌渲染 (V3.5)
# ==========================================

INPUT_PATH = "drafts/ai_analysis.json"
OUTPUT_PATH = "outputs/final_report.html"

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_sparkline_svg(prices, width=120, height=40):
    if not prices or len(prices) < 2: return "-"
    min_p, max_p = min(prices), max(prices)
    range_p = max_p - min_p if max_p != min_p else 1
    pts = []
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * width
        y = height - ((p - min_p) / range_p) * height
        pts.append(f"{x},{y}")
    path_data = " ".join(pts)
    color = "#059669" if prices[-1] >= prices[0] else "#dc2626"
    return f"""
    <svg width="{width}" height="{height}" viewBox="0 -5 {width} {height+10}" fill="none" xmlns="http://www.w3.org/2000/svg">
        <polyline points="{path_data}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="{pts[-1].split(',')[0]}" cy="{pts[-1].split(',')[1]}" r="3" fill="{color}"/>
    </svg>
    """

def build_html(result):
    print("[3/4] Generating AI Berkshire Master Report with Deep Gann...")
    
    gann_data = load_json("drafts/gann_analysis.json")

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Berkshire 終極投研報告</title>
        <style>
            :root {{
                --berkshire-navy: #111827;
                --primary: #1e3a8a; --secondary: #3b82f6; --bg: #f4f4f5; --card-bg: #ffffff;
                --text: #1f2937; --text-light: #6b7280; --positive: #059669; --negative: #dc2626;
                --neutral: #d97706; --border: #e5e7eb;
                --gann-gold: #854d0e; --gann-bg: #fffdf2;
            }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: var(--bg); color: var(--text); line-height: 1.7; margin: 0; padding: 2rem; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header-section {{ 
                text-align: center; margin-bottom: 3rem; padding: 4rem 2rem; 
                background: linear-gradient(135deg, #111827, #1e293b); color: white; 
                border-radius: 24px; box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1); 
            }}
            h1 {{ margin: 0 0 0.5rem 0; font-size: 3rem; font-weight: 800; letter-spacing: 1px; }}
            
            .section {{ background: var(--card-bg); border-radius: 20px; padding: 2.5rem; margin-bottom: 3rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }}
            .section-title {{ border-bottom: 4px solid var(--primary); padding-bottom: 0.75rem; margin-top: 0; margin-bottom: 2rem; color: var(--berkshire-navy); font-size: 1.8rem; font-weight: 800; }}
            
            .content-box {{ background-color: #f8fafc; border-left: 6px solid var(--primary); padding: 1.5rem; margin-bottom: 1.5rem; border-radius: 0 12px 12px 0; }}
            .content-box.strategy {{ border-left-color: var(--neutral); background-color: #fffbeb; }}
            .content-box.perspective {{ border-left-color: var(--secondary); background-color: #eff6ff; }}
            .content-box h4 {{ margin-top: 0; color: var(--primary); font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 700; }}
            .content-box p {{ margin: 0; font-size: 1.05rem; color: #374151; white-space: pre-wrap; }}
            
            table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 1rem; border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }}
            th, td {{ padding: 1.25rem 1rem; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle; }}
            th {{ background-color: #f9fafb; font-weight: 700; color: var(--berkshire-navy); }}
            
            /* Gann Card Styles */
            .gann-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; }}
            .gann-card {{ border: 1px solid #fde68a; border-radius: 20px; padding: 2rem; background: var(--gann-bg); position: relative; overflow: hidden; }}
            .gann-card::before {{ content: "GANN"; position: absolute; top: -10px; right: -10px; font-size: 5rem; font-weight: 900; color: rgba(133, 77, 14, 0.05); transform: rotate(-15deg); }}
            .gann-header {{ font-weight: 800; font-size: 1.4rem; color: var(--gann-gold); margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; }}
            
            .gann-sub-section {{ margin-bottom: 1.5rem; }}
            .gann-sub-title {{ font-size: 0.9rem; font-weight: 800; text-transform: uppercase; color: #a16207; border-bottom: 1px solid #fef08a; margin-bottom: 0.8rem; padding-bottom: 0.3rem; }}
            
            .retracement-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }}
            .retracement-item {{ background: white; padding: 10px; border-radius: 8px; border: 1px solid #fef08a; display: flex; justify-content: space-between; }}
            .retracement-label {{ font-size: 0.85rem; color: var(--text-light); }}
            .retracement-val {{ font-weight: 700; color: var(--berkshire-navy); }}
            
            .pyramiding-item {{ background: #166534; color: white; padding: 12px; border-radius: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }}
            .pyramiding-level {{ font-size: 0.8rem; background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; }}
            
            .status-pivot {{ color: var(--gann-gold); font-weight: bold; background: #fef9c3; padding: 2px 6px; border-radius: 4px; }}
            .sentiment-1 {{ color: var(--positive); font-weight: bold; background: #d1fae5; padding: 6px 12px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>AI Berkshire 終極投研報告</h1>
                <p>四大師核心對抗 ｜ 數據源：whatmkreallysaid.com ｜ 核心趨勢與江恩幾何雙週刊</p>
                <p>報告產生時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">🕵️‍♂️ 四大師總經與產業對抗綜述</h2>
                {f'<div class="content-box"><h4>📉 宏觀經濟與護城河檢視</h4><p>{result.get("macro_summary")}</p></div>' if result.get('macro_summary') else ''}
                {f'<div class="content-box strategy"><h4>🎯 四大師建議策略</h4><p>{result.get("investment_direction")}</p></div>' if result.get('investment_direction') else ''}
                {f'<div class="content-box perspective"><h4>💡 核心投資觀點 (QA 心法)</h4><p>{result.get("core_perspective")}</p></div>' if result.get('core_perspective') else ''}
            </div>

            <div class="section">
                <h2 class="section-title" style="color: var(--gann-gold);">📐 江恩幾何技術預測與加碼策略</h2>
                <div class="gann-container">
                {"".join([f'''
                    <div class="gann-card">
                        <div class="gann-header">
                            <span>{g['name']} ({g['symbol']})</span>
                            <span style="font-size: 1rem; color: var(--text);">現價: {g['current_price']}</span>
                        </div>
                        
                        <div class="gann-sub-section">
                            <div class="gann-sub-title">💎 核心加碼點位建議 (Gann Pyramiding)</div>
                            {"".join([f'<div class="pyramiding-item"><span class="pyramiding-level">{p["level"]}</span><span style="font-weight:800; font-size:1.1rem;">{p["price"]}</span><span style="font-size:0.8rem; opacity:0.9;">{p["desc"]}</span></div>' for p in g['pyramiding']]) if g['pyramiding'] else '<p style="font-size:0.9rem; color:var(--text-light);">暫無特定加碼訊號</p>'}
                        </div>

                        <div class="gann-sub-section">
                            <div class="gann-sub-title">📉 波段百分比回檔防守位 (2025/04 基準)</div>
                            <div class="retracement-grid">
                                {"".join([f'<div class="retracement-item"><span class="retracement-label">{k}</span><span class="retracement-val">{v}</span></div>' for k,v in g['retracements'].items()])}
                            </div>
                        </div>

                        <div class="gann-sub-section">
                            <div class="gann-sub-title">🌀 江恩正方形幾何位階 (Square of 9)</div>
                            {"".join([f'<div style="display:flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dashed #fef08a;"><span>{lvl["angle"]}° {("<span class status-pivot>🎯 關鍵</span>" if lvl["status"]=="pivot" else "")}</span><span style="font-weight:bold;">{lvl["price"]}</span></div>' for lvl in g['levels']])}
                        </div>
                    </div>
                ''' for g in gann_data]) if gann_data else '<p>無江恩數據</p>'}
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📊 標的價值分級與動能回測</h2>
                <table>
                    <thead>
                        <tr>
                            <th>標的名稱</th>
                            <th>AI 判定</th>
                            <th>🔥 提及頻次</th>
                            <th>【四大師綜合判定與 Mirror Test】</th>
                            <th>📈 1M 趨勢</th>
                            <th style="text-align:right;">現價/漲跌</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for stock in result.get('stocks', []):
        sentiment_map = {1: "PASS (優質)", 0: "GRAY (觀察)", -1: "FAIL (避開)"}
        perf = stock.get('performance')
        counts = stock.get('counts', {'1m': 0, '3m': 0, '6m': 0})
        price_html = f'<div style="text-align:right;"><div style="font-weight:800;">{perf["end_price"]:.2f}</div><div style="color:{"#059669" if perf["pct_change"] >=0 else "#dc2626"}; font-weight:700;">{perf["pct_change"]:+.2f}%</div></div>' if perf else '<div style="text-align:right; color:#9ca3af;">無報價</div>'
        svg_html = generate_sparkline_svg(perf.get('price_history', [])) if perf else '-'
        
        html += f"""
            <tr>
                <td><strong>{stock['name']}</strong><br><span style="font-size:0.8rem; background:#f3f4f6; padding:2px 4px; border-radius:4px;">{stock['ticker']}</span></td>
                <td><span class="sentiment-{stock['sentiment']}">{sentiment_map.get(stock['sentiment'], "未知")}</span></td>
                <td style="font-size:0.85rem; font-weight:bold;">1M:{counts['1m']} | 3M:{counts['3m']}</td>
                <td style="max-width:400px; font-size:0.9rem; color:#4b5563;">{stock['reason']}</td>
                <td>{svg_html}</td>
                <td>{price_html}</td>
            </tr>
        """
        
    html += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[3/4] Success! AI Berkshire Master Report (V3.5) rendered to {OUTPUT_PATH}")

if __name__ == "__main__":
    data = load_json(INPUT_PATH)
    build_html(data)
