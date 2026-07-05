import json
from datetime import datetime
import os

# ==========================================
# 模組三：AI Berkshire 品牌渲染 (Rendering)
# ==========================================

INPUT_PATH = "drafts/ai_analysis.json"
OUTPUT_PATH = "outputs/final_report.html"

def load_json(path):
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
    print("[3/4] Generating AI Berkshire Master Report...")
    
    gann_data = []
    try:
        if os.path.exists("drafts/gann_analysis.json"):
            with open("drafts/gann_analysis.json", 'r', encoding='utf-8') as f:
                gann_data = json.load(f)
    except:
        pass

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
                --gann-gold: #854d0e;
            }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: var(--bg); color: var(--text); line-height: 1.7; margin: 0; padding: 2rem; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header-section {{ 
                text-align: center; margin-bottom: 3rem; padding: 4rem 2rem; 
                background: linear-gradient(135deg, #111827, #1e293b); color: white; 
                border-radius: 24px; box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1); 
            }}
            h1 {{ margin: 0 0 0.5rem 0; font-size: 3rem; font-weight: 800; letter-spacing: 1px; }}
            .header-section p {{ color: #9ca3af; font-size: 1.2rem; }}
            
            .section {{ background: var(--card-bg); border-radius: 20px; padding: 2.5rem; margin-bottom: 3rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }}
            .section-title {{ border-bottom: 4px solid var(--primary); padding-bottom: 0.75rem; margin-top: 0; margin-bottom: 2rem; color: var(--berkshire-navy); font-size: 1.8rem; font-weight: 800; }}
            
            .content-box {{ background-color: #f8fafc; border-left: 6px solid var(--primary); padding: 2rem; margin-bottom: 2rem; border-radius: 0 12px 12px 0; }}
            .content-box.strategy {{ border-left-color: var(--neutral); background-color: #fffbeb; }}
            .content-box.perspective {{ border-left-color: var(--secondary); background-color: #eff6ff; }}
            .content-box h4 {{ margin-top: 0; color: var(--primary); font-size: 1.4rem; margin-bottom: 1rem; font-weight: 700; }}
            .content-box.strategy h4 {{ color: var(--neutral); }}
            .content-box.perspective h4 {{ color: var(--secondary); }}
            .content-box p {{ margin: 0; font-size: 1.1rem; color: #374151; white-space: pre-wrap; }}
            
            table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 1.5rem; border: 1px solid var(--border); border-radius: 16px; overflow: hidden; }}
            th, td {{ padding: 1.25rem 1rem; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle; }}
            th {{ background-color: #f9fafb; font-weight: 700; color: var(--berkshire-navy); font-size: 1rem; }}
            tr:last-child td {{ border-bottom: none; }}
            tr:hover {{ background-color: #f9fafb; }}
            
            .sentiment-1 {{ color: var(--positive); font-weight: bold; background: #d1fae5; padding: 6px 12px; border-radius: 8px; }}
            .sentiment-0 {{ color: var(--neutral); font-weight: bold; background: #fef3c7; padding: 6px 12px; border-radius: 8px; }}
            .sentiment--1 {{ color: var(--negative); font-weight: bold; background: #fee2e2; padding: 6px 12px; border-radius: 8px; }}
            
            .ticker-box {{ background: #f3f4f6; padding: 4px 8px; border-radius: 6px; font-family: monospace; font-weight: 700; font-size: 0.9rem; color: #4b5563; }}
            .reason-cell {{ max-width: 400px; line-height: 1.6; color: #4b5563; font-size: 0.95rem; }}
            
            .badge-container {{ display: flex; gap: 8px; }}
            .badge {{ padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; }}
            .badge-1m {{ background: #fee2e2; color: #b91c1c; }}
            .badge-3m {{ background: #fef3c7; color: #b45309; }}
            .badge-6m {{ background: #e0f2fe; color: #0369a1; }}
            
            .gann-card {{ border: 1px solid #fde68a; border-radius: 16px; padding: 1.5rem; background: #fffdf2; }}
            .gann-header {{ font-weight: 800; font-size: 1.3rem; color: var(--gann-gold); margin-bottom: 1rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>AI Berkshire 終極投研報告</h1>
                <p>四大師對抗矩陣 ｜ 數據源：whatmkreallysaid.com ｜ 近 14 天雙週特輯</p>
                <p>報告產生時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">🕵️‍♂️ 四大師總經與產業對抗綜述</h2>
                {f'<div class="content-box"><h4>📉 宏觀經濟與護城河檢視</h4><p>{result.get("macro_summary")}</p></div>' if result.get('macro_summary') else ''}
                {f'<div class="content-box strategy"><h4>🎯 四大師建議策略</h4><p>{result.get("investment_direction")}</p></div>' if result.get('investment_direction') else ''}
                {f'<div class="content-box perspective"><h4>💡 核心投資觀點 (QA 心法)</h4><p>{result.get("core_perspective")}</p></div>' if result.get('core_perspective') else ''}
            </div>

            <div class="section">
                <h2 class="section-title">📐 江恩幾何技術預測</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                {"".join([f'''
                    <div class="gann-card">
                        <div class="gann-header">{g['name']} <span style="font-size: 0.9rem; font-weight: normal;">({g['symbol']})</span></div>
                        <div style="margin-bottom: 1rem; font-weight: bold;">現價: {g['current_price']}</div>
                        {"".join([f'<div style="display:flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #e5e7eb;"><span>{lvl["angle"]}°</span><span style="font-weight:bold;">{lvl["price"]}</span></div>' for lvl in g['levels']])}
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
                <td><strong>{stock['name']}</strong><br><span class="ticker-box">{stock['ticker']}</span></td>
                <td><span class="sentiment-{stock['sentiment']}">{sentiment_map.get(stock['sentiment'], "未知")}</span></td>
                <td>
                    <div class="badge-container">
                        <span class="badge badge-1m">1M:{counts['1m']}</span>
                        <span class="badge badge-3m">3M:{counts['3m']}</span>
                    </div>
                </td>
                <td class="reason-cell">{stock['reason']}</td>
                <td style="min-width: 130px;">{svg_html}</td>
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
    print(f"[3/4] Success! AI Berkshire Master Report rendered to {OUTPUT_PATH}")

if __name__ == "__main__":
    import os
    data = load_json(INPUT_PATH)
    build_html(data)
