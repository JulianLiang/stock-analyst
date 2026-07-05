---
name: gann-analysis
description: Use this skill for W.D. Gann technical analysis on stocks, indices, futures, forex, or any traded instrument — Gann angles/fan lines, Square of 9, Square of 144, Gann time cycles, and price-time symmetry projections. Applies to individual stocks as well as macro/index-level analysis (e.g. S&P 500, Dow, Hang Seng, TAIEX) — not to raw macroeconomic data series like GDP/CPI/interest rates themselves. Trigger this whenever the user mentions "江恩", "Gann", "Gann angles/fan", "Square of 9", "Square of 144", asks for support/resistance levels derived from a pivot high/low (for a stock OR an index/大盤), asks for time-cycle turning-point dates, or wants a price-time forecast using geometric/numerological methods rather than standard indicators (MA, RSI, MACD). Also use when the user gives a price and/or date and asks "what are the next Gann levels" or "when is the next time cycle turn."
---

# 江恩分析 (W.D. Gann Analysis)

本 skill 提供 W.D. Gann 技術分析方法論的完整工具組，包括江恩角度線、江恩正方形（Square of 9 / Square of 144）、時間週期分析，以及價格-時間對稱預測。

## 核心原則（先讀這段再動手）

江恩理論建立在幾個核心假設上，動手計算前務必先跟使用者確認或自行判斷：

1. **價格與時間可以互換（Price = Time）**：江恩認為當價格波動幅度與時間經過的單位數相等時，會出現重要的支撐/壓力/轉折。這是江恩角度線的理論基礎。
2. **一切依附在一個「有效樞紐點」(pivot) 上**：所有計算都從一個關鍵高點、低點，或使用者指定的起始價/起始日期開始。**沒有明確的樞紐點，江恩分析就無法進行** —— 這是第一個必須跟使用者確認的東西。
3. **這是一套機率/機率性框架，不是精確預測工具**：在輸出結果時，適度提醒這些是「潛在關注位」而非保證會發生的價位或日期，避免使用者誤解為確定性預測。
4. **正方形類方法（Square of 9 / 144）對「起始數字」和「刻度單位」高度敏感**：同一檔標的用不同起始點或不同刻度（1點/1檔/1%），算出來的關鵗價位會完全不同。務必先確認使用者要用什麼基準。

## 開始前先確認三件事

在動手計算之前，透過對話（不需要每次都用表單式提問，直接在文字中確認即可）釐清：

1. **樞紐點**：使用者要分析的關鍵高點/低點價格是多少？對應日期是？（如果使用者只給了「現在的股價」，可以用最近的顯著高/低點，或請使用者指定）
2. **想要哪一種分析**：角度線（趨勢線型）、正方形（支撐壓力價位）、時間週期（轉折日期），還是三者都要？
3. **標的特性**：股票 vs 期貨 vs 加密貨幣，價格量級差異很大（例如 3 元的股票和 30000 元的比特幣），會影響角度線的刻度單位怎麼設定。

如果使用者的請求已經包含足夠資訊（例如直接給了樞紐價格和日期，且明確說要哪種分析），不需要重複確認，直接計算並說明所用假設即可。

## 適用範圍：個股 / 指數（總經）/ 純經濟數據

這個 skill 的計算方法適用於**任何有可交易價格走勢的標的**，但不適用於**純經濟數據本身**。動手前先判斷使用者問的是哪一種：

- **個股**：完全適用，這是江恩理論原本設計的對象。給定股票的樞紐高/低點，即可套用角度線、正方形、時間週期三種工具。
- **指數／大盤（總經層面的市場觀察）**：完全適用，且是常見的「總經」應用方式 —— 例如加權指數、標普 500、道瓊、恆生指數等。指數本身就是有市場價格的商品，樞紐點、角度線、Square of 9、時間週期都能直接套用，跟分析個股的方法完全相同，差別只在於樞紐點通常是大盤的歷史高低點。
- **期貨、外匯、加密貨幣**：同樣適用，方法一致，差異主要在角度線的刻度單位設定（見 `references/gann_angles.md` 的「刻度單位怎麼定」）。
- **純經濟數據（GDP、CPI、失業率、利率等指標數字本身，而非追蹤這些指標的可交易商品）**：**不建議套用**。原因是江恩的支撐/壓力/角度線概念，前提是「這是一個有人在買賣、會因資金流與心理反應在特定價位有反應」的市場價格；經濟數據本身沒有這種市場機制，Square of 9 的平方根旋轉法雖然數學上可以套在任何數字，但脫離價格意義後解釋力很薄弱。遇到使用者想拿裸經濟數據做江恩分析時，可以說明這個限制，並詢問是否其實是想分析「反映該總經數據的某個指數或商品」（例如用美國十年期公債殖利率的價格走勢，而非只是利率決策的百分比數字本身）。
- **總經事件作為樞紐點觸發因子**：這完全沒問題，而且是常見做法。例如「FOMC 決議後大盤創新高」可以拿這個高點當樞紐點，只是後續計算對象仍是該指數/商品的價格，而不是利率數字本身。

## 三大工具總覽

| 工具 | 用途 | 需要輸入 | 詳細方法見 |
|---|---|---|---|
| 江恩角度線 (Gann Fan) | 由樞紐點畫出多條不同斜率的趨勢線，作為動態支撐/壓力 | 樞紐價格、樞紐日期、價格/時間刻度單位 | `references/gann_angles.md` |
| 正方形 (Square of 9 / 144) | 由基準數字算出等角度分佈的價位，作為靜態支撐/壓力目標價 | 基準價格（樞紐高點或低點） | `references/square_of_9.md` |
| 時間週期 (Time Cycles) | 由樞紐日期往後推算可能的轉折日期 | 樞紐日期 | `references/time_cycles.md` |

**執行順序建議**：先讀對應的 reference 檔案取得完整公式與細節，再進行計算。三份 reference 檔案彼此獨立，只讀使用者需要的部分即可，不用每次都全讀。

## 計算工具

`scripts/square_of_9.py` 可直接執行，輸入一個基準價格即可算出 8 個主要角度（0°/45°/90°/135°/180°/225°/270°/315°/360°）對應的價位，包含基本角（0°/90°/180°/270°，江恩稱為 cardinal cross，通常視為較強的支撐壓力）與對角（45°/135°/225°/315°，ordinal cross，通常視為次要關注位）。用法：

```bash
python3 scripts/square_of_9.py <基準價格> [--rings N]
```

角度線與時間週期目前沒有現成腳本（因為高度依賴使用者給的刻度單位與樞紐日期選擇），請依 reference 檔案中的公式手算或用 bash 寫一次性計算。

## 輸出格式（依情況彈性決定）

依對話脈絡選擇最合適的呈現方式，不要每次都用同一種：

- **快速詢問「下一個江恩價位是多少」**：直接在對話中用文字/表格回答即可，不需要建立檔案或圖表。
- **完整的角度線 + 正方形 + 時間週期綜合分析**：適合用 Visualizer 畫一張圖表（股價走勢 + 角度扇線疊加，或正方形環狀圖），搭配文字說明。畫圖前記得先呼叫 `visualize:read_me`（`chart` 或 `diagram` 模組）。
- **使用者要保存、比對多檔標的、或要做成監控用的清單**：用 xlsx skill 建立試算表（樞紐價、各角度價位、對應日期），方便使用者持續更新。動手前先讀 `/mnt/skills/public/xlsx/SKILL.md`。
- **使用者要一份完整分析報告（例如要給別人看）**：用 docx skill 產出正式文件。動手前先讀 `/mnt/skills/public/docx/SKILL.md`。

不確定要哪種格式時，預設用對話文字回答，並在最後主動問一句「要不要幫你做成圖表/表格？」而不是先花時間做圖表。

## 免責聲明提醒

在提供具體價位或日期預測時，簡短提醒這些是根據江恩幾何/數字理論推導的「潛在關注區間」，屬於技術分析framework 的一種觀點，不構成投資建議，市場實際走勢仍需搭配其他驗證。不需要每次長篇大論，一句話帶過即可。
