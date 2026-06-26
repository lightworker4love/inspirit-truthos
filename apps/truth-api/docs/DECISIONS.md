# docs/DECISIONS.md

# in spirit AI Architecture Decisions Log

- 檔案編號：ISP-OPS-ARCH-003
- 文件名稱：Architecture Decisions Log
- 文件類型：Architecture
- 文件狀態：Active
- 版本號：v1.0
- 建立日期：2026-03-16
- 最後更新：2026-03-16
- 作者：Light Worker / in spirit AI

---

## 1. 目的

本文件用於記錄本機治理層與相關 ops 系統的重要架構決策。

本文件回答的不是「做了什麼」，而是：
- 為什麼這樣設計
- 當時有哪些替代方案
- 最後選擇了哪一條路
- 這個決策保護了什麼

---

## 2. 使用原則

每當出現以下情況，應新增一條 decision record：

- 新的架構分層被確立
- 系統責任邊界被重新定義
- 重要資料流或權限流被調整
- 重要 ops 制度被固化
- 關鍵部署與治理策略被定案

---

## 3. Decision Records

## DEC-001：將 truth-api 定位為 policy boundary layer

- 狀態：Accepted
- 日期：2026-03-16

### Context
平台需要在 OpenClaw Gateway 之前建立一層本機治理邊界，以處理身份、角色、模型政策與審計，而不讓所有請求直接進入 runtime layer。

### Decision
將 truth-api 定位為 policy boundary layer，負責身份驗證、角色約束、模型政策查找、thread 與 audit 生命週期管理。

### Consequences
- 治理責任與執行責任分離。
- 架構更容易排障與交接。
- 未來可在不重寫 Gateway 的前提下調整治理規則。

---

## DEC-002：保留 OpenClaw Gateway 作為 runtime / orchestration layer

- 狀態：Accepted
- 日期：2026-03-16

### Context
平台已具備本機 OpenClaw 主鏈路，適合作為模型提供者整合、代理執行與 runtime 路由核心。

### Decision
不以 truth-api 取代 OpenClaw，而是保留 OpenClaw Gateway 作為 runtime / orchestration layer。

### Consequences
- 避免治理與執行混層。
- 保留 OpenClaw 生態與既有主鏈路優勢。
- 降低整體改動面與維護成本。

---

## DEC-003：以角色化模型路由承接模型能力治理

- 狀態：Accepted
- 日期：2026-03-16

### Context
同一組模型能力不應對所有身份無差別暴露，平台需要把模型能力放回角色、責任與 mode 的治理脈絡中。

### Decision
採用角色化模型路由，使模型可用性由角色與 mode 共同決定。

### Consequences
- 模型能力成為治理對象，而非裸露資源。
- 權限邏輯更可持續擴充。
- 未來更容易支援多角色、多租戶或多場景治理。

---

## DEC-004：將 thread / entry / audit 沉澱為個案記錄庫

- 狀態：Accepted
- 日期：2026-03-16

### Context
平台的互動不應只是一次性問答，而應能回到連續性的個案脈絡中。

### Decision
將 thread、entry、audit 等互動資料視為個案記錄庫核心，而不只是單純技術資料表。

### Consequences
- 系統具備可追溯與可回看能力。
- 個案互動可被放回生命歷程脈絡。
- 未來更適合建立長期陪伴與治理記憶。

---

## DEC-005：將 ops 報表與 runbooks 視為 operational memory

- 狀態：Accepted
- 日期：2026-03-16

### Context
若只有腳本與 log，系統雖能運行，但知識很難交接，也很難累積成制度。

### Decision
將 daily / weekly / monthly / incident 報表、runbooks、index、manifest、architecture docs 視為 operational memory layer。

### Consequences
- 系統從「能跑」進化為「能被記得」。
- incident learning 可累積。
- operator field 開始形成。

---

## DEC-006：以正式文件編號與總索引治理文件系統

- 狀態：Accepted
- 日期：2026-03-16

### Context
文件數量成長後，若沒有編號規則與索引入口，知識很容易散落並失去辨識性。

### Decision
建立正式檔案編號規則與 `docs/INDEX.md` 作為文件系統的治理樞紐。

### Consequences
- 文件身份清楚。
- 新文件更容易納入管理。
- 文件系統更適合長期擴充與交接。

---

## 4. 建議決策格式

未來新增 decision 時，建議使用以下格式：

## DEC-XXX：Decision Title

- 狀態：Proposed / Accepted / Superseded / Deprecated
- 日期：YYYY-MM-DD

### Context
...

### Decision
...

### Consequences
...

### Alternatives Considered
...

---

## 5. 狀態定義

- `Proposed`：提出中，尚未定案
- `Accepted`：已採納，為現行有效決策
- `Superseded`：已被新決策取代
- `Deprecated`：不再建議採用，但保留歷史參考價值

---

## 6. 原則

當系統愈來愈複雜，
真正會拯救未來團隊的，
不是只有架構圖，
而是當時為何做出這個選擇的清楚記錄。
