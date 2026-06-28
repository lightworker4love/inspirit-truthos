# in spirit AI 平台
# 本機治理層建設歷程總覽

---

## 封面資訊

- 檔案編號：ISP-OPS-ARCH-001
- 文件名稱：本機治理層建設歷程總覽
- 文件英文名：Local Governance Layer Build Overview
- 文件類型：內部架構與治理歷程文件
- 文件層級：Internal
- 文件狀態：Approved Draft / 正式初版
- 版本號：v1.1
- 建立日期：2026-03-16
- 最後更新：2026-03-16
- 作者（Author）：Light Worker / in spirit AI
- 審閱者（Reviewer）：________________
- 核准者（Approver）：________________
- 所屬專案：inspirit-truthos / truth-api / Local Governance Layer
- 適用環境：Mac mini 本機治理環境
- 適用範圍：truth-api、OpenClaw Gateway、本機角色化模型路由、本機個案記錄治理、ops 記憶化體系

---

## 文件目的

本文件旨在說明 in spirit 本機治理層的建設歷程，整理其從服務入口、身份閘門、角色化模型路由，到個案記錄與運維記憶化的完整演化脈絡。

本文件不處理程式碼與執行指令，而聚焦於：
- 建設背景
- 架構定位
- 治理意圖
- 里程碑演進
- 後續治理方向

---

## 適用範圍

本文件適用於以下場景：

- truth-api 作為 policy boundary layer 的本機部署脈絡
- OpenClaw Gateway 作為 runtime/orchestration layer 的本機主鏈路
- 個案身份閘門、角色化模型路由、個案記錄庫的治理設計
- daily / weekly / monthly / incident 為核心的 ops 記憶化治理機制
- 後續交接、回顧、架構對齊與治理演進討論

---

## 不適用範圍

本文件不涵蓋以下內容：

- 程式碼實作細節
- shell / Makefile / launchd 實際指令
- 資料表 schema 細節
- API request/response 規格
- 特定 bug 的逐步排障流程

上述內容應由技術規格文件、runbooks、incident 文件與 ops scripts 文件承接。

---

## 一頁摘要

這套本機治理層的建設，核心不是增加一個普通 API，而是在 OpenClaw Gateway 前方長出一個清楚的 policy boundary layer，讓身份、角色、模型能力與個案記錄能夠在本機形成秩序。

其演化主線可概括為三件事：

1. 建立個案身份閘門，讓系統先辨識「誰在進入」。
2. 建立角色化模型路由，讓系統決定「他可以走哪條模型路徑」。
3. 建立個案記錄庫與 ops 記憶節奏，讓系統記得「這次互動在個案生命史中的位置」。

---

## 里程碑摘要

### 里程碑 M1：治理入口成形
確立 truth-api 作為本機治理入口，並放置於 OpenClaw Gateway 之前，使系統開始具備 policy boundary 與 runtime layer 的分工。

### 里程碑 M2：身份閘門建立
從單純服務存活檢查，提升到身份與角色辨識，讓所有請求不再被視為匿名流量。

### 里程碑 M3：角色化模型路由
建立角色與 mode 對模型能力的映射，使模型路由進入治理範疇，而非裸露資源調用。

### 里程碑 M4：個案記錄庫形成
thread、entry、audit 等資料沉澱為個案歷程基礎，使互動開始具備連續性與可追溯性。

### 里程碑 M5：ops 記憶化
日報、週報、月報、incident postmortem、runbooks index、ops architecture 等文件逐步成形，使治理層從「能運作」提升到「能被記得、被理解、被交接」。

---

## 版本變更紀錄

| 版本 | 日期 | 作者 | 變更摘要 |
|---|---|---|---|
| v1.0 | 2026-03-16 | Light Worker | 初版建立，完成本機治理層歷程敘事與正式內部文件格式。 |
| v1.1 | 2026-03-16 | Light Worker | 補上檔案編號、版本變更紀錄、關聯檔案與名詞定義表，升級為企業級範本。 |
| vNext | YYYY-MM-DD | ______ | 待補充。 |

---

## 關聯檔案

### 上位說明文件
- `README-dev.md`
- `README-prod.md`
- `README-ops-rhythm.md`
- `README-runbooks-index.md`

### 架構與治理文件
- `docs/ops-architecture.md`
- `incident-checklist.md`
- `rotate-secrets.md`

### ops 節奏與報表文件
- daily reports
- weekly summaries
- monthly summaries
- incident postmortems
- runbook manifest

### 補充技術文件
- 本機身份與角色路由規格文件
- 個案記錄庫 schema 文件
- 模型政策與 mode 映射文件
- 未來治理演進 roadmap 文件

---

## 正文

## 一、建設背景

這套本機治理層的出發點，來自一個關鍵判斷：當平台已經具備 OpenClaw Gateway 主鏈路之後，問題就不再只是模型能不能回應，而是身份、角色、權限與記錄如何形成秩序。

因此，系統要處理的不只是推理結果，而是：
- 誰可以進來
- 以什麼角色被辨識
- 可走哪條模型路徑
- 這次互動如何被放回個案生命脈絡中

---

## 二、核心架構定位

整個建設過程中最重要的架構決定，是讓 truth-api 成為 policy boundary layer，而讓 OpenClaw Gateway 保持為 runtime / orchestration layer。

這種分工使得：
- 身份驗證留在治理層
- 角色約束留在治理層
- 模型政策查找留在治理層
- 執行與上游模型調用留在 OpenClaw 主鏈路

這代表系統從「服務入口」進化為「治理入口」。

---

## 三、治理層三大能力

### 1. 個案身份閘門
系統不再把所有流量視為無差別請求，而是先確認「這是誰」以及「這個身份屬於哪個角色位置」。

### 2. 角色化模型路由
模型能力不再是裸露資源，而是必須經過角色與 mode 的治理映射，才能決定可走的路徑。

### 3. 個案記錄庫
thread、entry、audit 不只是資料儲存，而是將互動沉澱為可回看、可追溯、可歸屬的個案歷程。

---

## 四、本機化的意義

這套治理層以本機方式長出，不只是部署選擇，而是一種治理選擇。

當本機已具備：
- OpenClaw Gateway 主鏈路
- 本機 control plane
- LaunchAgent 節奏化運行
- reports / runbooks 記憶化體系

則治理層貼著本機主鏈路形成，會比外掛到遠端服務更一致、更可控，也更利於事故時分層排查。

---

## 五、從治理到運維記憶

在基礎治理邊界形成後，系統逐步長出另一層更深的能力：運維記憶。

這包括：
- daily awareness
- weekly reflection
- monthly pattern recognition
- incident learning
- runbook indexing
- architecture narration

也因此，整個系統從「能跑」走向「能被理解」，再從「能被理解」走向「能被交接」。

---

## 六、建設成果的本質

若以平台精神來看，這段建設真正完成的，不只是本機驗證、角色路由與記錄存放，而是一個讓 AI 回到關係秩序中的治理容器。

在這個容器裡：
- 身份先於能力
- 角色先於模型
- 記錄先於遺忘
- 節奏先於混亂
- 邊界先於失控

這也是本機治理層最核心的價值。

---

## 七、後續方向

下一階段不應只是增加更多腳本，而應持續朝以下方向成熟：

- 更高層的全域可觀測性
- 更清楚的治理節奏與責任歸屬
- 更穩定的文件交接能力
- 更可持續的 incident learning 機制
- 更一致的 policy boundary 與 runtime boundary 分工

當這些條件成立，系統就不再只是工程成果，而會逐漸成為一套制度化治理基礎。

---

## 名詞定義表

| 名詞 | 定義 |
|---|---|
| 本機治理層 | 位於本機平台內、負責身份、角色、權限、記錄與治理邏輯的邊界層。 |
| policy boundary layer | 以規則、角色、身份與模型政策為主的治理邊界層。 |
| runtime layer | 真正負責模型調用、代理執行與路由運作的執行層。 |
| 個案身份閘門 | 先辨識使用者身份與角色，再允許請求進入系統的治理入口。 |
| 角色化模型路由 | 根據角色與 mode 決定可使用模型與路徑的治理機制。 |
| 個案記錄庫 | 將 thread、entry、audit 等互動沉澱成可追蹤個案歷程的資料層。 |
| ops 記憶化 | 將 daily、weekly、monthly、incident 等營運軌跡轉化為可回顧文件的能力。 |
| operator field | 由服務、節奏、報表、runbooks 與 incident learning 組成的操作性記憶場。 |
| runbook | 在故障、變更、巡檢或治理情境下可被遵循的操作文件。 |
| incident postmortem | 將事故經過、根因、修復與後續改善沉澱成可回顧文件的機制。 |

---

## 文件管理規則

- 本文件應作為治理總覽文件維護，不直接承載程式碼與指令。
- 所有重大架構變更應更新「版本變更紀錄」。
- 若治理層責任邊界有變動，需同步更新「關聯檔案」與「名詞定義表」。
- 若新增新的 ops 節奏或新類型 runbook，應納入本文件的里程碑摘要或關聯檔案列表。

---

## 文件結語

本文件不是用來證明系統做了多少，而是用來確保未來回頭看時，仍知道這套本機治理層為何而建、如何成形、保護了什麼，以及下一步應往哪裡走。
