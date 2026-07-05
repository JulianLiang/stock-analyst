import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import concurrent.futures

# --- 股票分類矩陣 ---
PORTFOLIO = {
    "🏆 買入首選 (安全邊際與深厚護城河)": [
        {"symbol": "2317.TW", "name": "鴻海", "reason": "全場唯一 Forward PE 低於 12 倍的巨頭，規模壁壘無可取代，下行風險已充分定價。"},
        {"symbol": "6414.TW", "name": "樺漢", "reason": "工業智聯網轉型成功 (ESaaS)，極高客戶轉換成本，ROE 穩定且 PE 僅 12 倍。"},
        {"symbol": "3324.TWO", "name": "雙鴻", "reason": "水冷散熱絕對贏家，交出近 29% ROE，在散熱族群中享有合理的估值優勢。"},
        {"symbol": "8299.TWO", "name": "群聯", "reason": "掌握 IP 矽智財的儲存軍火商，ROE 達 37%，順利轉型 AI 企業級市場。"}
    ],
    "🟡 灰度觀察 (偉大企業，但等待好價格)": [
        {"symbol": "2330.TW", "name": "台積電", "reason": "絕對定價權的印鈔機，但目前估值透支未來，等待大盤回調至合理 PE 建倉。"},
        {"symbol": "2308.TW", "name": "台達電", "reason": "不碰低毛利代工，專注綠能/車用/散熱，完美商業模式但價格已定價未來3年成長。"},
        {"symbol": "2449.TW", "name": "京元電子", "reason": "純測試中立性與高轉換成本，需密切留意 323 億天價資本支出帶來的折舊風險。"},
        {"symbol": "3661.TW", "name": "世芯-KY", "reason": "EPS 轉換能力極強，但需防範雲端巨頭自研晶片成熟後的長期 NRE 掉單盲點。"},
        {"symbol": "2891.TW", "name": "中信金", "reason": "財管與信用卡護城河極深，十年確定性高。等待 P/B 回落至 1.5x 附近加碼。"},
        {"symbol": "2885.TW", "name": "元大金", "reason": "台股 ETF 與經紀業務特許現金牛。"},
        {"symbol": "2376.TW", "name": "技嘉", "reason": "估值便宜但受制於晶片原廠，毛利偏低的組裝廠，適合波段操作不宜價值長投。"}
    ],
    "🚬 深度價值 (菸屁股與資產清算)": [
        {"symbol": "2474.TW", "name": "可成", "reason": "P/B 僅 0.8，買的是帳上千億現金，下檔無風險，但管理層資本配置效率極低。"}
    ],
    "❌ 芒格否決 (價值陷阱、缺乏定價權或泡沫)": [
        {"symbol": "2454.TW", "name": "聯發科", "reason": "PE 飆高但缺乏消費者轉換成本，手機市場紅海競爭，不具備安全邊際。"},
        {"symbol": "3443.TW", "name": "創意", "reason": "估值極度昂貴 (PE>50x)，護城河獲利轉換力不如世芯。"},
        {"symbol": "5871.TW", "name": "中租-KY", "reason": "中國與東協延滯率壞帳黑天鵝難料，違反巴菲特「不賠錢」鐵律。"},
        {"symbol": "2327.TW", "name": "國巨", "reason": "重資產與景氣循環零組件，高估值將面臨嚴重的戴維斯雙殺。"},
        {"symbol": "2344.TW", "name": "華邦電", "reason": "記憶體價格接受者，同業對比下 ROE 與營益率優於旺宏，但仍屬景氣陷阱。"},
        {"symbol": "2337.TW", "name": "旺宏", "reason": "本業陷入嚴重虧損，毛利僅 25%，完全喪失定價權的落後者。"},
        {"symbol": "2408.TW", "name": "南亞科", "reason": "標準型 DRAM 大宗商品，低本益比是景氣反轉向下的危險訊號。"},
        {"symbol": "4919.TW", "name": "新唐", "reason": "併購效益遲滯，車用 MCU 復甦無期，本業營業虧損。"},
        {"symbol": "6223.TWO", "name": "旺矽", "reason": "探針卡絕對霸主，但 60 倍 PE 已將未來 5 年的完美預期透支完畢。"},
        {"symbol": "2383.TW", "name": "台光電", "reason": "CCL 龍頭護城河深，但估值過高，容錯率極低。"},
        {"symbol": "3037.TW", "name": "欣興", "reason": "載板跟隨 CoWoS 成長，但復甦緩慢且目前處於溢價區。"},
        {"symbol": "3406.TW", "name": "玉晶光", "reason": "被大立光壓制，且終端消費電子需求不穩。"},
        {"symbol": "3081.TWO", "name": "聯亞", "reason": "矽光子概念炒作，60倍PE面臨規格變動的高風險。"},
        {"symbol": "6451.TW", "name": "訊芯-KY", "reason": "純題材炒作，本業呈現虧損 (Op Margin -5%)，無內在價值基礎。"},
        {"symbol": "3483.TWO", "name": "力致", "reason": "營益率僅 1%，卻享有 40 倍 PE 的散熱幻想股。"},
        {"symbol": "6789.TW", "name": "采鈺", "reason": "估值高達 70 倍脫離地心引力。"},
        {"symbol": "5371.TWO", "name": "中光電", "reason": "紅色供應鏈重擊，ROE 趨近於零。"},
        {"symbol": "3149.TW", "name": "正達", "reason": "常年虧損，無競爭力。"},
        {"symbol": "8422.TW", "name": "可寧衛", "reason": "特許掩埋場印鈔機，但掩埋空間耗盡風險未除，目前報價無安全邊際。"}
    ]
}

def fetch_data(item):
    symbol = item["symbol"]
    try:
        info = yf.Ticker(symbol).info
        price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        pe = info.get('forwardPE', 0)
        pb = info.get('priceToBook', 0)
        roe = info.get('returnOnEquity', 0)
        om = info.get('operatingMargins', 0)
        
        item['price'] = f"{price:.2f}" if price else "-"
        item['pe'] = f"{pe:.1f}x" if pe else "-"
        item['pb'] = f"{pb:.2f}x" if pb else "-"
        item['roe'] = f"{roe*100:.1f}%" if roe else "-"
        item['om'] = f"{om*100:.1f}%" if om else "-"
    except Exception as e:
        item['price'], item['pe'], item['pb'], item['roe'], item['om'] = "-", "-", "-", "-", "-"
    return item

def generate_html_email(data_dict):
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f5; margin: 0; padding: 20px; color: #1f2937; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #111827, #374151); color: #ffffff; padding: 40px 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 1px; }}
            .header p {{ margin: 10px 0 0 0; color: #9ca3af; font-size: 14px; }}
            .content {{ padding: 30px; }}
            .intro {{ background: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px 20px; margin-bottom: 30px; border-radius: 0 8px 8px 0; font-size: 15px; color: #166534; line-height: 1.6; }}
            
            .category-title {{ margin-top: 40px; margin-bottom: 15px; font-size: 20px; font-weight: bold; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
            
            /* Specific Category Colors */
            .cat-buy {{ color: #059669; border-color: #059669; }}
            .cat-hold {{ color: #d97706; border-color: #d97706; }}
            .cat-value {{ color: #4f46e5; border-color: #4f46e5; }}
            .cat-veto {{ color: #dc2626; border-color: #dc2626; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
            th {{ background-color: #f9fafb; font-weight: 600; color: #4b5563; white-space: nowrap; }}
            tr:hover {{ background-color: #f3f4f6; }}
            
            .sym-badge {{ display: inline-block; background: #e5e7eb; padding: 2px 6px; border-radius: 4px; font-size: 12px; color: #4b5563; font-weight: bold; margin-bottom: 4px; }}
            .stock-name {{ font-size: 15px; font-weight: bold; color: #111827; }}
            .reason-text {{ color: #4b5563; line-height: 1.5; font-size: 13px; max-width: 350px; }}
            
            .metric-val {{ font-weight: 600; color: #1f2937; }}
            .footer {{ background: #f9fafb; text-align: center; padding: 20px; font-size: 12px; color: #6b7280; border-top: 1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 AI Berkshire 終極總評報告</h1>
                <p>四大師對抗視角｜台股核心 30 檔資產分級矩陣</p>
                <p>Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            </div>
            
            <div class="content">
                <div class="intro">
                    <strong>系統提示：</strong> 本次報告匯總了近期對於台股四大梯隊的嚴格檢視。透過巴菲特（護城河）、芒格（逆向防守）、段永平（商業本質）與李錄（長期確定性）的框架，我們無情地剔除了缺乏定價權的代工廠、高估值的泡沫科技股以及景氣陷阱。以下為最終決策矩陣。
                </div>
    """
    
    # Mapping classes for styling
    color_map = {
        "🏆 買入首選 (安全邊際與深厚護城河)": "cat-buy",
        "🟡 灰度觀察 (偉大企業，但等待好價格)": "cat-hold",
        "🚬 深度價值 (菸屁股與資產清算)": "cat-value",
        "❌ 芒格否決 (價值陷阱、缺乏定價權或泡沫)": "cat-veto"
    }

    for category, stocks in data_dict.items():
        css_class = color_map.get(category, "")
        html += f'<h2 class="category-title {css_class}">{category}</h2>'
        html += """
        <table>
            <thead>
                <tr>
                    <th>標的</th>
                    <th>現價</th>
                    <th>Fwd P/E</th>
                    <th>P/B</th>
                    <th>ROE</th>
                    <th>Op Mgn</th>
                    <th>大師點評 (核心邏輯)</th>
                </tr>
            </thead>
            <tbody>
        """
        for s in stocks:
            html += f"""
                <tr>
                    <td>
                        <span class="stock-name">{s['name']}</span><br>
                        <span class="sym-badge">{s['symbol']}</span>
                    </td>
                    <td class="metric-val">{s['price']}</td>
                    <td class="metric-val">{s['pe']}</td>
                    <td class="metric-val">{s['pb']}</td>
                    <td class="metric-val">{s['roe']}</td>
                    <td class="metric-val">{s['om']}</td>
                    <td class="reason-text">{s['reason']}</td>
                </tr>
            """
        html += "</tbody></table>"

    html += """
            </div>
            <div class="footer">
                <p>Disclaimer: 本報告由 AI Berkshire 投研框架自動生成，利用量化數據與價值投資哲學進行評估，不構成實際投資建議。請投資人自行控管風險。</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print("Fetching live financial metrics for 30 stocks...")
    
    # Flatten list and fetch in parallel
    all_tasks = []
    for cat_stocks in PORTFOLIO.values():
        all_tasks.extend(cat_stocks)
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(fetch_data, all_tasks))
        
    html_content = generate_html_email(PORTFOLIO)
    
    print("\nPreparing to send Email...")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD")
    receiver_emails_str = "julians900724@gmail.com"

    if not sender_email or not sender_password:
        print("⚠️ 缺少 Email 環境變數，中止寄送。")
        return

    subject = f"【AI Berkshire 終極總評】台股核心 30 檔資產分級與買賣決策矩陣 ({datetime.now().strftime('%Y-%m-%d')})"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"AI Berkshire Framework <{sender_email}>"
    msg["To"] = receiver_emails_str
    
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email successfully sent to {receiver_emails_str}!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    main()
