import json
import re
import urllib.parse
from datetime import datetime, timezone
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from dateutil import parser

# ==========================================
# 模組一：資料萃取與正規化 (Data Extraction)
# ==========================================

CONFIG_PATH = "brain/config.json"
OUTPUT_PATH = "drafts/raw_episodes.json"
INDEX_URL = "https://whatmkreallysaid.com/episodes.json"
TODAY = datetime.now(timezone.utc)

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_transcript(text, config):
    if not text:
        return ""
    text = re.sub(r'##\s*贊助.*?(?=##|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'https?://\S+', '', text)
    ad_pattern = re.compile(
        r'.*(折扣碼|優惠碼|NordVPN|植村秀|東璧堂|蝦皮|團購|輸入碼|官方網站|點擊連結|結帳輸入|專屬優惠|本集節目由).*',
        re.IGNORECASE | re.MULTILINE
    )
    cleaned_text = re.sub(ad_pattern, '', text)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # 透過 Brain (知識腦) 進行字典正規化
    for nick, real_name in config.get("nicknames", {}).items():
        cleaned_text = cleaned_text.replace(nick, real_name)
        
    return cleaned_text.strip()

def fetch_notes_metadata(max_episodes):
    print(f"[1/4] Fetching index from: {INDEX_URL}")
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    response = requests.get(INDEX_URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    data.sort(key=lambda x: x.get('number', 0), reverse=True)
    return data[:max_episodes]

def extract_content_from_note(ep_meta, config):
    filename = ep_meta.get('filename')
    if not filename: return None
    url = f"https://whatmkreallysaid.com/episodes/{urllib.parse.quote(filename)}"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        pub_date_str = ep_meta.get('date')
        pub_date = parser.parse(pub_date_str).astimezone(timezone.utc).isoformat() if pub_date_str else TODAY.isoformat()
        cleaned_text = clean_transcript(response.text, config)
        return {'title': ep_meta.get('title', 'Unknown'), 'published': pub_date, 'summary': cleaned_text}
    except Exception as e:
        return None

def main():
    config = load_config()
    ep_metadata = fetch_notes_metadata(config["scraping"]["max_episodes"])
    episodes = []
    
    print(f"[1/4] Parallel extracting {len(ep_metadata)} episodes...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_content_from_note, meta, config) for meta in ep_metadata]
        for future in concurrent.futures.as_completed(futures):
            ep_data = future.result()
            if ep_data and len(ep_data['summary']) > 50:
                episodes.append(ep_data)
                
    episodes.sort(key=lambda x: x['published'], reverse=True)
    
    # 狀態存檔
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)
    print(f"[1/4] Success! Saved raw episodes to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()