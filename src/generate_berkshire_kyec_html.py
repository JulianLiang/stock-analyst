import os
from datetime import datetime

REPORT_PATH = "berkshire_kyec_report.html"

def generate_berkshire_html():
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Berkshire 投資決策備忘錄 - 京元電子 (2449.TW)</title>
        <style>
            :root {{
                --bg: #f8fafc;
                --card-bg: #ffffff;
                --text: #0f172a;
                --text-light: #475569;
                --border: #e2e8f0;
                --berkshire-red: #991b1b;
                --duan-blue: #1d4ed8;
                --buffett-green: #15803d;
                --munger-purple: #6b21a8;
                --lilu-orange: #b45309;
                --pass-green: #059669;
                --gray-orange: #d97706;
                --table-header: #f1f5f9;
            }}
            body {{
                font-family: 'Helvetica Neue', Arial, 'LiHei Pro', 'Microsoft JhengHei', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                line-height: 1.7;
                margin: 0;
                padding: 2rem;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            .header-section {{
                text-align: center;
                margin-bottom: 3rem;
                padding: 3rem 2rem;
                background: linear-gradient(135deg, #1e293b, #0f172a);
                color: white;
                border-radius: 16px;
                box-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.1);
            }}
            h1 {{ margin: 0 0 0.5rem 0; font-size: 2.5rem; letter-spacing: 1px; }}
            .subtitle {{ color: #94a3b8; font-size: 1.1rem; margin: 0; }}
            
            .section {{
                background: var(--card-bg);
                border-radius: 16px;
                padding: 2.5rem;
                margin-bottom: 2.5rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
            }}
            h2 {{
                border-bottom: 2px solid var(--border);
                padding-bottom: 0.75rem;
                margin-top: 0;
                font-size: 1.8rem;
                color: var(--berkshire-red);
            }}

            .data-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            .data-card {{
                background: #f8fafc;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid var(--border);
                text-align: center;
            }}
            .data-card span {{ display: block; color: var(--text-light); font-size: 0.95rem; margin-bottom: 0.5rem; }}
            .data-card strong {{ display: block; font-size: 1.5rem; color: var(--text); }}
            
            .agent-box {{
                margin-bottom: 2rem;
                padding: 1.5rem;
                border-radius: 12px;
                background-color: #f8fafc;
                border-left: 5px solid;
            }}
            .agent-box h3 {{ margin-top: 0; margin-bottom: 1rem; font-size: 1.3rem; display: flex; align-items: center; gap: 8px; }}
            .agent-box ul {{ margin: 0; padding-left: 1.5rem; color: var(--text-light); }}
            .agent-box li {{ margin-bottom: 0.5rem; }}
            
            .agent-duan {{ border-left-color: var(--duan-blue); }}
            .agent-duan h3 {{ color: var(--duan-blue); }}
            .agent-buffett {{ border-left-color: var(--buffett-green); }}
            .agent-buffett h3 {{ color: var(--buffett-green); }}
            .agent-munger {{ border-left-color: var(--munger-purple); }}
            .agent-munger h3 {{ color: var(--munger-purple); }}
            .agent-lilu {{ border-left-color: var(--lilu-orange); }}
            .agent-lilu h3 {{ color: var(--lilu-orange); }}

            .mirror-test {{
                background-color: #f0fdf4;
                border: 2px dashed #86efac;
                padding: 2rem;
                border-radius: 12px;
            }}
            .mirror-test ol {{ color: #14532d; font-weight: 500; font-size: 1.1rem; line-height: 1.8; }}
            .result-gray {{
                text-align: center;
                font-size: 2rem;
                font-weight: bold;
                color: var(--gray-orange);
                margin-top: 1.5rem;
                padding: 1rem;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgb(0 0 0 / 0.05);
            }}

            .conclusion-box {{
                background-color: #fffbeb;
                padding: 2rem;
                border-radius: 12px;
                border: 1px solid #fde68a;
            }}
            .conclusion-box h4 {{ margin-top: 1.5rem; margin-bottom: 0.5rem; color: var(--gray-orange); font-size: 1.2rem; }}
            .conclusion-box p {{ color: var(--text-light); margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-section">
                <h1>🎯 京元電 (2449.TW) 投資決策備忘錄</h1>
                <p class="subtitle">AI Berkshire Framework Analysis | 產生日期: {datetime.now().strftime("%Y-%m-%d")}</p>
            </div>

            <div class="section">
                <h2>▎核心財務體檢 (基於最新資料)</h2>
                <div class="data-grid">
                    <div class="data-card">
                        <span>毛利率 (Gross Margin)</span>
                        <strong>37.35%</strong>
                    </div>
                    <div class="data-card">
                        <span>本業營益率 (Op Margin)</span>
                        <strong>27.19%</strong>
                    </div>
                    <div class="data-card">
                        <span>股東權益報酬率 (ROE)</span>
                        <strong style="color: var(--buffett-green);">17.62%</strong>
                    </div>
                    <div class="data-card">
                        <span>預估本益比 (Forward P/E)</span>
                        <strong>21.73x</strong>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>▎四方大師觀點對決 (Multi-Agent Synthesis)</h2>
                
                <div class="agent-box agent-duan">
                    <h3>👤 段永平視角：對的生意嗎？ (Business Essence)</h3>
                    <ul>
                        <li><strong>本質與護城河：</strong> 半導體專業測試是一門極度依賴重資產與規模經濟的生意。雖然沒有網路效應，但它擁有極強的<strong>「轉換成本 (Switching Costs)」</strong>。當 Nvidia、AMD 或聯發科等大廠將測試程式與機台平台與京元電綁定後，要更換測試廠的驗證成本與良率風險極高。</li>
                        <li><strong>商業模式：</strong> 做為全球最大的純測試廠之一，其「中立性」是最大的無形資產。它不與客戶競爭封裝業務，能專心吞下 AI 晶片測試時間拉長（Testing Time）帶來的巨大紅利。</li>
                    </ul>
                </div>

                <div class="agent-box agent-buffett">
                    <h3>👴 巴菲特視角：護城河與估值安全邊際 (Moat & Valuation)</h3>
                    <ul>
                        <li><strong>財務體質強健：</strong> 2024 至 2025 年營收與淨利出現爆發性成長（淨利突破百億大關）。ROE 高達 17.6%，且常年維持近 40% 的毛利率與 27% 的營業利益率，證明其具備強大的護城河與定價能力。</li>
                        <li><strong>現金流隱患與資本配置：</strong> 最大警訊在於 2025 年的資本支出 (CapEx) 暴增至 323 億元，直接將原本正向的自由現金流打成 -192 億的負數。這顯示公司正在為吃下 AI 測試大單而瘋狂買入機台（如 Teradyne 等）。</li>
                        <li><strong>估值評價：</strong> Forward P/E 約 21.7 倍，對於一家處於強烈上升週期的硬體股來說，處於合理偏高的估值。目前並沒有出現「巴菲特式的絕佳安全邊際 (Margin of Safety)」。</li>
                    </ul>
                </div>

                <div class="agent-box agent-munger">
                    <h3>👓 查理·芒格視角：反過來想 (Inversion & Risks)</h3>
                    <ul>
                        <li><strong>快速否決清單 (Quick Veto List)：</strong> 如果這筆投資失敗，死穴在哪裡？死穴在於「過度擴張的資本支出遇上 AI 週期反轉」。如果 2026/2027 年 AI 晶片需求放緩，或者客戶改變晶片架構導致測試時間縮短，這 323 億元買進來的昂貴測試機台將面臨巨大的折舊壓力，瞬間壓垮獲利。</li>
                    </ul>
                </div>

                <div class="agent-box agent-lilu">
                    <h3>📈 李錄視角：十年確定性 (Civilization-level Trends)</h3>
                    <ul>
                        <li><strong>十年後它還會在嗎？</strong> 絕對會。隨著摩爾定律推進、先進封裝（CoWoS、Chiplet）興起，晶片內部結構越來越複雜。這意味著「測試 (Testing)」環節只會越來越長、要求越來越高。京元電站在了文明與科技演進的長坡厚雪上，十年確定性極高。</li>
                    </ul>
                </div>
            </div>

            <div class="section mirror-test">
                <h2>▎The Mirror Test (5句話買入邏輯挑戰)</h2>
                <ol>
                    <li>京元電是一門純測試的生意，受惠於先進封裝與 AI 晶片複雜度提升帶來的測試時間拉長紅利。</li>
                    <li>它的護城河來自於龐大的規模經濟、機台調度能力以及極高的客戶轉換成本。</li>
                    <li>財務體質極其優異，毛利率 37%、ROE 17.6% 傲視多數半導體中下游同業。</li>
                    <li>唯一隱患是為迎接大單而產生破紀錄的資本支出（323億），導致短期自由現金流轉負。</li>
                    <li>Forward P/E 21倍屬於合理估值，它是一家偉大的公司，但目前缺乏足夠的安全邊際來重倉。</li>
                </ol>
                <div class="result-gray">Result: 🟡 GRAY AREA (灰度觀察區)</div>
            </div>

            <div class="section conclusion-box">
                <h2>▎最終結論與操作建議 (Forced Conclusion)</h2>
                
                <h4>判定：GRAY AREA (好公司，但需等待好價格)</h4>
                <p>在 AI Berkshire 的框架下，京元電 (2449) 無疑是一門**「對的生意」**。它擁有完美的賽道（AI 晶片測試需求暴增）、深厚的護城河（客戶轉換成本極高），以及亮眼的獲利能力（ROE 17.6%）。然而，巴菲特視角與芒格視角對其 2025 年高達 323 億元的資本支出提出警告：重資產擴張期的 FCF 轉負是必然的痛，若伴隨未來 21 倍以上的 Forward P/E，這筆交易容錯率較低。</p>

                <h4>針對不同投資者的具體建議：</h4>
                <ul>
                    <li><strong>穩健型 / 保守型 (Steady/Conservative)：</strong> 不建議在歷史高估值區間與高資本支出期進場。耐心等待大盤系統性回調，或公司財報因折舊短暫拖累獲利時（導致 PE 降低至 12~15 倍區間）再行建倉。</li>
                    <li><strong>積極型 (Aggressive)：</strong> 認可「盈餘成長能覆蓋折舊」的邏輯。可動用部分資金建倉，但必須密切監控未來的「產能利用率」與「AI 客戶訂單能見度」。若出現客戶砍單的雜音，需果斷停損，因龐大的折舊費用將成為雙面刃。</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Successfully generated HTML report at: {REPORT_PATH}")

if __name__ == "__main__":
    generate_berkshire_html()
