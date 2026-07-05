import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

# ==========================================
# 模組四：核准閘門與 Email 寄送 (Governed Dispatch)
# ==========================================

INPUT_PATH = "outputs/final_report.html"

def send_summary_email(html_content):
    print("\n[4/4] 準備發送 Email...")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD")
    receiver_emails_str = os.environ.get("RECEIVER_EMAIL", "julians900724@gmail.com,dracohsieh@gmail.com")

    if not sender_email or not sender_password:
        print("⚠️ 警告：缺少 SENDER_EMAIL 或 SMTP_PASSWORD 環境變數，跳過發信。")
        sys.exit(0)

    # 【強制人工核准閘門 Typed Approval Gate】
    print("\n" + "="*50)
    print("🚦 報告已生成完畢，準備寄送給訂閱者。")
    print(f"📄 請先開啟 {INPUT_PATH} 檢查報告內容。")
    print("="*50)
    
    approval = input("如果您確認內容無誤，請輸入 'APPROVE' 以授權發信 (輸入其他字元將取消): ")
    if approval.strip() != "APPROVE":
        print("\n❌ 發信已取消 (原因：未獲得人類批准)。")
        sys.exit(2)
        
    print("\n⏳ 已獲得授權，正在連線 SMTP 伺服器發信...")

    subject = f"【股癌量化風向】兩週雙週報：最新標的熱度與波段績效追蹤 ({datetime.now().strftime('%Y-%m-%d')})"
    receiver_list = [email.strip() for email in receiver_emails_str.split(",")]
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_list)
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email 成功寄送給: {', '.join(receiver_list)}")
    except Exception as e:
        print(f"❌ 發信失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not os.path.exists(INPUT_PATH):
        print(f"❌ 找不到 HTML 報告: {INPUT_PATH}")
        sys.exit(1)
        
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    send_summary_email(html_content)