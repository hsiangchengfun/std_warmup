# 自主程式碼優化 Agent — 實作報告

## 一、專案目標

提供一個讓學生練習 **LLM-based agent** 的框架。
學生的任務不是自己優化程式碼,而是寫一個 agent 去呼叫 LLM 自動優化。

---

## 二、系統架構

```
project/
├── baseline/task.py         # O(n²) 三步驟管線 — 刻意慢、不可改
├── benchmark/eval.py        # 正確性檢查 + 分數計算
├── runner/run.py            # 主執行迴圈
├── agent/agent_template.py  # 學生要填的 skeleton(LLM client 已包好)
└── data/input.json          # 5000 個整數,deterministic
```

模組之間解耦:baseline 是 ground truth,benchmark 比對輸出與計時,
runner 把 agent 產出的 `candidate.py` 自動載入評估。

---

## 三、LLM 服務

- 端點:`https://portal.genai.nchc.org.tw/api/v1/chat/completions`
- 認證:`x-api-key` header(用 `requests` 直接打,不靠 OpenAI SDK)
- 模型:`Llama-3.1-8B-Instruct`(NCHC 提供,免費)
- 已內建 429 retry-with-backoff 與 401 診斷訊息

---

## 四、評分機制

```
score = baseline_time / candidate_time   (輸出正確)
score = 0                                (輸出錯誤)
```

| 分數 | 等級 |
|---|---|
| `< 2×` | D |
| `2–10×` | C |
| `10–100×` | B |
| `100–1000×` | A |
| `> 1000×` | A+ |

---

## 五、學生要做的事

在 `agent/agent_template.py` 把四個 `NotImplementedError` 填好:

1. **`propose_code`** — 組 prompt、呼叫 LLM、抽出 ```python``` 區塊
2. **`write_candidate`** — 寫進 `agent/candidate.py`
3. **`evaluate`** — 呼叫 `benchmark.eval.evaluate(...)`
4. **`run`** — 主迴圈,追蹤最佳分數,處理 LLM 錯誤

`call_llm()` 與 `log()` 已實作好,所有中間執行內容都會印到 console。

---

## 六、執行方式

```bash
export NCHC_API_KEY=...
pip install -r requirements.txt
python runner/run.py
```

---

## 七、設計重點

- **可重現**:固定 random seed 的 input,deterministic 評分
- **可觀察**:每一步都印 prompt / LLM 回應 / 抽出的 code / 評估結果
- **教學導向**:baseline 故意慢、benchmark 不可改、agent 邏輯留給學生
- **0 成本**:用 NCHC 免費模型即可完成作業
