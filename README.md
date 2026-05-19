# 作業:自主優化 Agent

## 一、作業目標

實作一個 **LLM-based 自主優化 agent**,讓它自己讀懂一段慢的 Python 程式碼,
自己呼叫 LLM 改寫成更快但等效的版本,自己跑 benchmark 驗證結果,並重複迭代,
最終取得最高分數。

> 你的工作 **不是** 自己優化 `baseline/task.py`。
> 你的工作是寫一個 agent,讓 agent 去優化它。

---

## 二、環境設定

本作業預設使用 **OpenRouter** 當 LLM 入口 — 一支 key 可以切換 Claude / GPT /
Gemini / Llama 等所有 model,而且**有免費 model 可用,$0 也能完成作業**。

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 註冊 OpenRouter 並拿 API key
#    https://openrouter.ai/keys
export OPENROUTER_API_KEY=sk-or-...

# 3. 先跑一次確認 baseline 能動
python runner/run.py
```

此時還沒有 agent,runner 會用 baseline 自己跟自己比,分數穩定在 1.0 附近。

### Model 選擇

打開 `agent/agent_template.py`,在 `Agent.__init__` 改 `self.model`:

| Model | 費用 | 預期分數天花板 |
|---|---|---|
| `openai/gpt-oss-20b:free` (預設) | $0 | ~5–10× |
| `google/gemini-2.0-flash` | 便宜 | ~50× |
| `openai/gpt-4o-mini` | 便宜 | ~50× |
| `anthropic/claude-haiku-4-5` | 中等 | ~100× |
| `anthropic/claude-sonnet-4-6` | 較貴 | ~500×+ |

**建議**:先用 free 模型把流程通,再用付費模型衝高分。OpenRouter 註冊送 $1
試用額度,加上 free 模型,沒花錢也能拿到不錯的成績。

---

## 三、你要實作的東西

開啟 `agent/agent_template.py`,把所有 `raise NotImplementedError` 的方法填好。

### 每一輪 (iteration) agent 要做的事

```
1. 讀目前的程式碼  ──► baseline/task.py (第一輪) 或 agent/candidate.py (之後)
2. 組 prompt      ──► 包含目前 code + 上一輪的分數/錯誤訊息
3. 呼叫 LLM       ──► Claude API,拿到改寫建議
4. 解析回應       ──► 從 markdown 中抽出 ```python ... ``` 區塊
5. 寫入 candidate.py
6. 跑 benchmark   ──► from benchmark.eval import evaluate
7. 記錄結果       ──► 保留歷代最佳;失敗就帶錯誤訊息進下一輪
```

### 對應的方法

| 方法 | 你要做的事 |
|---|---|
| `__init__` | 已內建 OpenRouter client。你可以再加路徑、歷史紀錄、best-score tracker |
| `call_llm(prompt)` | 已實作好(透過 OpenRouter)。可以加 retry、timeout、token 計數 |
| `propose_code(current_code, last_result)` | 組 prompt → call_llm → 解析回應 → 回傳純 Python source |
| `write_candidate(code)` | 把 source 寫進 `agent/candidate.py` |
| `evaluate()` | 載入 candidate,呼叫 `benchmark.eval.evaluate(...)`,回傳結果 dict |
| `run()` | 主迴圈,重複 propose → write → evaluate,追蹤 best_score |

---

## 四、評分標準

### 4.1 自動評分

跑完你的 agent 後,看 `runner/run.py` 印出的 **best_score**:

| 分數 | 等級 | 說明 |
|---|---|---|
| `0` | F | LLM 改壞了,輸出跟 baseline 對不上 |
| `< 2×` | D | agent 沒做出有效優化 |
| `2× – 10×` | C | 局部優化(例如改了其中一個 step) |
| `10× – 100×` | B | 多個 step 都換成更好的演算法 |
| `100× – 1000×` | A | 完整重寫成 O(n) 或更好 |
| `> 1000×` | A+ | 演算法層級的重寫,接近極限 |

### 4.2 程式設計與報告

- agent 結構清楚、容易閱讀
- 有處理 LLM 回傳壞 code 的情況(語法錯誤、跑超時、輸出錯誤)
- 有保留歷代最佳結果的機制
- 簡短報告(1–2 頁)說明:
  - 你的 prompt 策略
  - 哪一輪取得突破?LLM 做了什麼改動?
  - 收斂曲線(每一輪的分數)
  - 遇到的失敗案例與處理方式

---

## 五、提交要求

繳交一個 zip 檔,包含:

```
your_id/
├── agent/agent_template.py    # 你填完的 agent
├── agent/candidate.py         # 最後一次 LLM 產出的 code(最佳版本)
├── log.txt                    # runner 完整輸出
└── report.pdf                 # 1–2 頁報告
```

**不要修改** `baseline/`、`benchmark/`、`data/`、`runner/` 任何檔案。

---

## 六、提示與常見陷阱

### Prompt 設計
- 把 baseline source code 直接貼進 prompt 是最簡單的起點
- 明確要求「輸出必須完全等於原本的 `run_task` 結果」
- 失敗時把錯誤訊息或 timing 結果回灌進下一輪 prompt

### 安全與穩定性
- LLM 可能輸出無限迴圈 → 用 `signal.alarm` 或 subprocess timeout 包住評估
- LLM 可能輸出 syntax error → `try/except` 包住載入步驟
- LLM 可能輸出對的演算法但細節錯 → 必定要跑 `evaluate()` 驗證,別只信它說好

### Agent 策略
- **單純策略**:每輪都拿目前 candidate 給 LLM 繼續改
- **rollback 策略**:如果新版分數變低,丟掉、用舊版繼續
- **多臂策略**:讓 LLM 一次提多個版本,挑最好的留下

