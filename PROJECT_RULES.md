# PROJECT_RULES.md
# TruthOS Project Rules for Human Engineers

## 1. 這個專案是什麼

`inspirit-truthos` 是 in spirit AI 的語意推理核心。

它不是一般聊天機器人後端，也不是單純的向量資料庫展示專案。  
它是一個面向「反思、辨識、生命模式理解」的 **Truth-oriented reasoning system**。

TruthOS 的主要任務是幫使用者從：

- 情緒糾結
- 生命模式重複
- 限制性信念
- 關係失衡
- 自我誤解

移動到：

- 更清楚的自我理解
- 更正確的責任邊界
- 更穩定的反思能力
- 更 grounded 的下一步行動

它是 in spirit AI 裡「AI Mentor + Second Me + Life Knowledge Platform」的核心語意引擎。這個平台原本就被定義為一套「可長期陪伴、可記憶、可治理」的人類意識支援系統，而不是一般聊天產品。:contentReference[oaicite:0]{index=0}

---

## 2. 專案的核心世界觀

### 2.1 TruthOS 追求的不是更會講，而是更會辨識
我們不把流暢度當成最高目標。  
TruthOS 更重視：

- grounded output
- structured reasoning
- graceful degradation
- clear observability

而不是：

- 花俏語言
- 模型自信亂講
- 單一路徑依賴
- 出錯即全掛

### 2.2 TruthOS 的使命是「在不完美條件下仍保留意義」
這是專案最重要的哲學。

若某層失效，系統應退化，但不能直接死亡。  
這跟你平台原本「高信任、可治理、可追溯」的方向一致。

### 2.3 不把推論包裝成真理
你的平台已經明確提出「有道理未必是真理」這個覺幻原則。:contentReference[oaicite:2]{index=2}  
因此專案中的任何模型輸出，都應避免：

- 把猜測講成定論
- 把風格化敘事講成事實
- 把 metaphysical language 當作免責胡扯通行證

---

## 3. 架構原則

TruthOS 採分層設計，且各層責任要清楚。

### 3.1 結構層分工

- **SQLite**  
  結構化真理資料與 fallback source of truth

- **LanceDB**  
  高精度語意檢索層  
  用於 truth puzzles / methods / principle retrieval  
  不是一般聊天記憶層

- **OpenClaw / gateway**  
  模型路由層  
  管 embedding / provider path / fallback path

- **OpenAI Python client**  
  應用程式端 API client  
  負責 embeddings / model calls

- **FastAPI**  
  對外應用層與 reasoning API

這和你原本的整體系統藍圖相容：  
Second Me 是體驗層，Mem0 + Qdrant 是廣域記憶層，LanceDB 是高精度方法論記憶子系統，OpenClaw 是行動與代理層。

### 3.2 LanceDB 的定位不能漂移
LanceDB 在本專案中不是「多一個 vector DB 而已」。  
它扮演的是：

- 高精度 truth puzzle index
- 方法論 / 原則檢索層
- 經驗與結構化智慧檢索層

一句話：

**Qdrant / Mem0 是廣域雲，LanceDB 是精準索引和鐵律驅動的智慧結晶。** :contentReference[oaicite:4]{index=4}

---

## 4. 不可妥協的可靠性規則

### 4.1 Gateway 壞掉，不等於 API 可以跟著殉道
若 OpenClaw routing 失敗，系統必須能：

- fallback 到官方 OpenAI endpoint
- 或進一步 fallback 到 SQLite keyword retrieval

### 4.2 沒有 LanceDB index，不代表整個 query endpoint 可以報廢
若向量索引不存在：

- 先嘗試自動建索引
- 若建索引失敗，改走 SQLite fallback
- 仍需回 usable reasoning response

### 4.3 `/api/truth/query` 不可因單點故障直接炸掉
無論底層走哪條路，輸出都應盡量維持：

- mirror
- truth_view
- coach_question
- action

### 4.4 所有容錯都必須可觀測
不要只做 fallback，不做觀測。  
至少要能知道目前：

- gateway 是否可用
- vector index 是否存在
- embedding 目前走 gateway / openai / sqlite
- retrieval 目前走 lancedb / sqlite

---

## 5. 允許的執行模式

TruthOS 至少要能穩定支援三種模式：

### Mode A — 完整語意模式
- OpenClaw 可用
- embeddings 可用
- LanceDB 可用

使用：
- gateway embeddings
- LanceDB retrieval

### Mode B — fallback 語意模式
- OpenClaw 壞掉
- 官方 OpenAI 可用
- LanceDB 可用

使用：
- OpenAI embeddings
- LanceDB retrieval

### Mode C — 降級推理模式
- embeddings 不可用
- LanceDB 不可用或缺失

使用：
- SQLite keyword retrieval
- reasoning composer 仍回傳 structured output

這是你目前 self-healing architecture 的核心，也是這個 repo 必須永遠保住的系統個性。

---

## 6. API 契約規則

### 6.1 `/healthz`
最少要回：

```json
{
  "status": "ok",
  "embedding_gateway": true,
  "vector_index": true,
  "embedding_mode": "gateway"
}
```

### 6.2 `/system/status`

這是運維觀測層，不是裝飾品。  
它應明確回傳目前路徑：

```json
{
  "gateway": "openclaw",
  "embedding": "gateway",
  "retrieval": "lancedb",
  "vector_index": true
}
```

### 6.3 `/api/truth/query`

輸出應維持結構化，不因內部 provider 差異而飄來飄去：

```json
{
  "mirror": "...",
  "truth_view": "...",
  "coach_question": "...",
  "action": "...",
  "dimension": "...",
  "principles": ["..."],
  "retrieval_mode": "lancedb",
  "embedding_mode": "gateway"
}
```

### 6.4 degraded mode 也要像個系統，不要像事故現場

若走 SQLite fallback，仍應提供：

- 基本 dimension 判斷
- 合理的 principle / puzzle 對應
- 可用的 reasoning composer 結果

---

## 7. 資料模型規則

目前專案核心語意資料由以下組成：

- 12 truth dimensions
- 100 core principles
- 1200 truth puzzles

這是目前的 semantic minimum viable core。  
這些資料不是 demo 裝飾，而是 reasoning engine 的語意地基。

### 7.1 Schema 不可隨意漂移

不要隨便重新命名核心欄位，除非有 migration 計畫。  
重點表包括：

- `truth_dimensions`
- `core_principles`
- `truth_puzzles`
- `belief_logs`
- `blind_spot_archives`

### 7.2 `embedding_text` 是首選向量化欄位

不要直接拿 `statement` 取代 `embedding_text`。  
`embedding_text` 的價值在於它能包住：

- dimension
- principle
- contextual keywords
- reframed meaning

這會顯著提高檢索品質。

### 7.3 資料擴充要遵守「知識原子化」

未來新增資料時，應優先做成：

- principle
- puzzle
- relation
- reflection prompt
- pattern note

而不是只追加長文章。

---

## 8. Retrieval 設計規則

### 8.1 預設 pipeline

推薦順序：

- dimension classifier
- semantic retrieval
- principle selection
- reasoning composer

### 8.2 fallback 順序

不可亂改：

- LanceDB vector search
- auto-build LanceDB index
- SQLite keyword fallback

### 8.3 top_k 不要亂縮

目前建議預設：

- `top_k = 12`

在沒有測試前，不要隨便改成 `3` 或 `5`，那會讓語意覆蓋突然變薄。

### 8.4 reranking 是未來升級，不是現在拆台

未來若加 reranker，必須是加法，不是破壞原本 base retrieval。  
建議未來做法：

- retrieve top 40
- rerank to top 8–12
- compose response

---

## 9. Reasoning 設計規則

TruthOS 的 response 結構固定以四段為核心：

- mirror
- truth_view
- coach_question
- action

定義

`mirror`  
先照見使用者當下處境，而不是立刻糾正對方

`truth_view`  
點出較深的模式、盲點或原則

`coach_question`  
打開自我覺察，不替使用者代答

`action`  
提供一個 grounded 的下一步，而不是宇宙空話

重點

不要把回應寫成：

- 全是高維形容詞
- 全是空泛鼓勵
- 全是模型自戀散文

TruthOS 的風格應該是：

- reflective
- clear
- grounded
- actionable

---

## 10. OpenClaw、OpenAI client、LanceDB 的關係規則

### 10.1 OpenClaw 不等於 repo 依賴已完整

這點很重要，因為很容易搞混。

OpenClaw 是 gateway / router / CLI

`openai` Python 套件是 app 端 client

`lancedb` Python 套件是向量存取層

所以：

本機有 OpenClaw ≠ 這個 repo 已具備可重現依賴

### 10.2 可重現性優先於「我電腦上剛好有裝」

所有本 repo 執行需要的依賴，都必須出現在：

- `apps/truth-api/requirements.txt`

至少包括：

- `openai>=1.0`
- `lancedb`
- `pandas`
- `pyarrow`
- `numpy`
- `tqdm`
- `python-dotenv`

### 10.3 嵌入管線必須是雙 provider 設計

embedding pipeline 預設應該：

- 先試 gateway
- 失敗就 fallback OpenAI
- 再失敗就退 SQLite retrieval

---

## 11. 安全與維運規則

### 11.1 不可洩漏 secrets

任何修改都不得讓以下資訊裸露在 log / response 中：

- API keys
- tokens
- credentials
- local machine secret paths

### 11.2 不能削弱既有 guardrails

你的平台原本已有安全 sprint 與 guardrails / redaction 基線。

7️⃣777-Platform Security Sprint…

修改 repo 時，不得：

- 繞過 redaction
- 偷關閉 guardrails
- 讓高風險操作默默通過

### 11.3 Logs 要有用，但不能變成洩密日誌

需要能觀測 routing / fallback / retrieval mode，  
但不能因此把敏感 payload 全噴出來。

---

## 12. 變更管理規則

### 12.1 先小改，後重構

盡量：

- 小步提交
- 不破壞既有可跑流程
- 讓每次改動都可驗證

### 12.2 大改之前要先說明

如果要大改，先交代：

- current behavior
- proposed behavior
- risk
- migration impact

### 12.3 檔案責任要清楚

目前重要檔案責任如下：

`gateway_check.py`  
gateway health / routing detection

`embedding_pipeline.py`  
embedding provider orchestration

`vector_index.py`  
LanceDB creation / validation / reuse

`retriever.py`  
retrieval and fallback chain

`reasoning.py`  
response synthesis

`main.py`  
API surface

`scripts/build_vector_index.py`  
vector build entrypoint

不要把所有東西都塞回 `main.py`，那會很快變成神秘黑盒子。

---

## 13. 測試規則

至少要有以下驗證：

- Python compile check
- vector build command
- `/healthz`
- `/system/status`
- `/api/truth/query`

推薦命令：

```bash
python -m compileall apps/truth-api/app scripts/build_vector_index.py
python scripts/build_vector_index.py
```

驗證重點不是「所有功能都完美」，  
而是：

在 degraded mode 下，系統仍可工作。

---

## 14. 專案語氣與邊界

這個專案重視：

- discernment
- reflective guidance
- system resilience
- long-term extensibility

避免把它做成：

- 普通 assistant demo
- 單純 spiritual flavor chatbot
- 過度工程化但沒有使用價值的框架玩具

這個專案的價值，在於它試圖回答你整個平台的文明級敘事：  
不是再做一個產品，而是在建立 AI 時代的人類意識基礎設施。

---

## 15. 宇宙憲法（Golden Rules）

### Rule 1

如果必須在「優雅失敗」和「整個炸掉」之間選，  
選優雅失敗。

### Rule 2

如果必須在「說得好聽」和「更接近真實」之間選，  
選更接近真實。

### Rule 3

如果 gateway 壞了、embedding 壞了、index 壞了，  
系統仍要盡可能保留 meaning。

### Rule 4

TruthOS 的目的不是看起來厲害，  
而是在不完美條件下，仍幫人保持清楚。

### Rule 5

不要讓工程實作背叛平台精神。  
技術層、產品層、意識層，應指向同一件事：  
讓 AI 成為長期、可治理、可辨識的陪伴與反思基礎設施。

---

## 給你的建議用法

現在你有兩份配對檔：

- `AGENTS.md`
- `PROJECT_RULES.md`

最好的擺法是：

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  AGENTS.md
  PROJECT_RULES.md
```

然後你可以在給 Codex 的任務裡再補一句：

Before making changes, read AGENTS.md and PROJECT_RULES.md and follow them as the repository constitution.

這樣不管是 agent 還是人類工程師，都是照同一套宇宙憲法工作，不會一邊修系統、一邊把靈魂拆掉。
