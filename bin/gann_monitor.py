import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

# ==========================================
# 監控模組：江恩變盤自動 Email 警報 (Gann Email Alert)
# ==========================================

MONITOR_TARGETS = {
    "0050.TW": {
        "name": "元大台灣50",
        "bull_trigger": 110.5,
        "bear_trigger": 106.5,
        "support": 103.5,
        "resistance": 114.0
    },
    "2330.TW": {
        "name": "台積電",
        "bull_trigger": 2545.0,
        "bear_trigger": 2390.0,
        "support": 2250.0,
        "resistance": 2640.0
    }
}

def send_alert_email(subject, body):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL", "julians900724@gmail.com,dracohsieh@gmail.com")
    
    if not sender_email or not sender_password:
        print("⚠️ 警告：未設定 Email 環境變數，無法發送警報。")
        return

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = f"Gann Monitor Alert <{sender_email}>"
    msg["To"] = receiver_email
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ 變盤警報已成功寄送至 {receiver_email}")
    except Exception as e:
        print(f"❌ Email 發送失敗: {e}")

def check_gann_status(symbol, data):
    conf = MONITOR_TARGETS[symbol]
    name = conf['name']
    recent_closes = data['Close'].tail(3).tolist()
    last_price = recent_closes[-1]
    
    status_code = "IDLE"
    status_text = "🟡 橫盤震盪中 (無明確轉折)"
    action = "持股觀望 / 靜待平衡"
    
    if all(p >= conf['bull_trigger'] for p in recent_closes):
        status_code = "BULL_CONFIRMED"
        status_text = "🟢 向上轉折確立 (Bullish Turn)"
        action = f"加碼進場 / 目標看至 {conf['resistance']}"
    elif all(p <= conf['bear_trigger'] for p in recent_closes):
        status_code = "BEAR_CONFIRMED"
        status_text = "🔴 向下轉折確立 (Bearish Turn)"
        action = f"減碼避險 / 下方支撐看至 {conf['support']}"
    elif last_price >= conf['bull_trigger']:
        status_code = "BULL_ATTEMPT"
        status_text = "🧪 向上嘗試中 (尚未確認)"
        action = "觀察明日收盤是否維持在點位之上"
    elif last_price <= conf['bear_trigger']:
        status_code = "BEAR_ATTEMPT"
        status_text = "⚠️ 向下回測中 (尚未確認)"
        action = "觀察明日收盤是否止跌"

    return {
        "symbol": symbol,
        "name": name,
        "price": f"{last_price:.2f}",
        "status_code": status_code,
        "status_text": status_text,
        "action": action
    }

def main():
    print(f"--- 啟動江恩變盤監控系統 ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---")
    
    alerts = []
    for symbol in MONITOR_TARGETS:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="5d")
            if data.empty: continue
            
            res = check_gann_status(symbol, data)
            print(f"[{res['name']}] 現價: {res['price']} | 狀態: {res['status_text']}")
            
            # 只要不是 IDLE (橫盤)，就加入警報清單
            if res['status_code'] != "IDLE":
                alerts.append(res)
                
        except Exception as e:
            print(f"Error checking {symbol}: {e}")

    # 若有任何警報訊號，發送 Email
    if alerts:
        subject = f"【🚨 江恩變盤警報】偵測到 {len(alerts)} 檔標的趨勢轉折訊號！"
        body = "偵測到以下標的發生幾何位階變動：\n\n"
        for a in alerts:
            body += f"● {a['name']} ({a['symbol']})\n"
            body += f"  - 當前價格: {a['price']}\n"
            body += f"  - 幾何狀態: {a['status_text']}\n"
            body += f"  - 建議行動: {a['action']}\n"
            body += "-" * 30 + "\n"
        body += f"\n檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        send_alert_email(subject, body)
    else:
        print("日內檢查完畢：目前所有標的均在幾何盤整區間，無須發送警報。")

if __name__ == "__main__":
    main()
