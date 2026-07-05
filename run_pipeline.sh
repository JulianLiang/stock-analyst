#!/bin/bash

# ==========================================
# 企業級自動化工作流 Orchestrator
# ==========================================

echo "🚀 啟動 AI Berkshire 分析管線..."

# 確保在正確的虛擬環境中執行
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Step 1: 萃取資料
python bin/01_extract_data.py
if [ $? -ne 0 ]; then
    echo "❌ 步驟 1 失敗，終止流程。"
    exit 1
fi

# Step 2: AI 分析與量化回測
python bin/02_analyze_with_ai.py
if [ $? -ne 0 ]; then
    echo "❌ 步驟 2 失敗，終止流程。"
    exit 1
fi

# Step 2.5: 江恩幾何技術分析
python bin/gann_intelligence_v3.py
if [ $? -ne 0 ]; then
    echo "❌ 步驟 2.5 (江恩分析) 失敗，終止流程。"
    exit 1
fi

# Step 3: 前端 HTML 與 SVG 渲染
python bin/03_render_html.py
if [ $? -ne 0 ]; then
    echo "❌ 步驟 3 失敗，終止流程。"
    exit 1
fi

# Step 4: 人工核准與發送
python bin/04_send_email.py
if [ $? -eq 2 ]; then
    echo "⏸️  發信遭人為阻擋，但報告已安全存放在 outputs/final_report.html。"
    exit 0
elif [ $? -ne 0 ]; then
    echo "❌ 步驟 4 (發信) 失敗。"
    exit 1
fi

echo "✨ 完整管線執行完畢！"