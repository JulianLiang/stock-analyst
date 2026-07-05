#!/bin/bash

# 1. 進入專案目錄
cd /Users/julian/Documents/gemini/stock-analyst

# 2. 載入環境變數 (Email 與 API Key)
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# 3. 執行監控腳本
source venv/bin/activate
python bin/gann_monitor.py >> logs/gann_monitor.log 2>&1

echo "Execution completed at $(date)" >> logs/gann_monitor.log
