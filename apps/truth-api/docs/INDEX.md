# docs/INDEX.md

# in spirit AI 文件總索引

- 檔案編號：ISP-OPS-INDEX-001
- 文件名稱：docs 文件總索引
- 文件類型：Index
- 文件狀態：Active
- 版本號：v1.0
- 建立日期：2026-03-16
- 最後更新：2026-03-16
- 作者：Light Worker / in spirit AI

---

## 1. 目的

本文件作為 in spirit AI 本機治理層、ops 系統、runbooks、架構文檔與階段性交付文件的統一索引入口。

使用本文件可快速回答：
- 這份文件在哪裡
- 它屬於哪一類
- 它目前狀態如何
- 應該先讀哪一份
- 哪些文件彼此關聯

---

## 2. 閱讀順序

### 新加入成員建議閱讀順序
1. `README-dev.md`
2. `README-prod.md`
3. `README-ops-rhythm.md`
4. `README-runbooks-index.md`
5. `docs/ops-architecture.md`
6. `ISP-OPS-ARCH-001_本機治理層建設歷程總覽.md`

### 發生 incident 時建議閱讀順序
1. `incident-checklist.md`
2. `README-prod.md`
3. `rotate-secrets.md`
4. 最新 daily / weekly / monthly reports
5. 最新 incident postmortem

---

## 3. 文件索引表

| 文件編號 | 文件名稱 | 路徑 | 類別 | 狀態 | 說明 |
|---|---|---|---|---|---|
| ISP-OPS-POLICY-001 | 檔案編號規則 | `docs/ISP-OPS-POLICY-001_檔案編號規則.md` | Policy | Active | 定義正式文件編號規則。 |
| ISP-OPS-INDEX-001 | docs 文件總索引 | `docs/INDEX.md` | Index | Active | 全站文件導航入口。 |
| ISP-OPS-ARCH-001 | 本機治理層建設歷程總覽 | `docs/ISP-OPS-ARCH-001_本機治理層建設歷程總覽.md` | Architecture | Active | 敘述本機治理層從身份、角色、記錄到 ops 記憶化的歷程。 |
| ISP-OPS-ARCH-002 | ops architecture | `docs/ops-architecture.md` | Architecture | Active | 說明 truth-api、OpenClaw、launchd、reports、runbooks 的分層架構。 |
| ISP-OPS-GUIDE-001 | ops rhythm | `README-ops-rhythm.md` | Guide | Active | 定義 daily / weekly / monthly / incident 節奏。 |
| ISP-OPS-INDEX-002 | runbooks index | `README-runbooks-index.md` | Index | Active | 列出主要 runbooks 與操作入口。 |
| ISP-OPS-GUIDE-002 | production guide | `README-prod.md` | Guide | Active | 生產環境操作與維護指引。 |
| ISP-OPS-GUIDE-003 | development guide | `README-dev.md` | Guide | Active | 開發與本機工作流指引。 |
| ISP-OPS-RUNBOOK-001 | incident checklist | `incident-checklist.md` | Runbook | Active | 事故發生時的第一時間操作清單。 |
| ISP-SEC-RUNBOOK-001 | secret rotation | `rotate-secrets.md` | Runbook | Active | secret 輪替、順序與回滾原則。 |
| ISP-OPS-REPORT-001 | Documentation & Governance Changelog | `docs/CHANGELOG.md` | Report | Active | 制度與文件演進時間軸。 |
| ISP-OPS-ARCH-003 | Architecture Decisions Log | `docs/DECISIONS.md` | Architecture | Active | 關鍵架構決策紀錄。 |
| ISP-TRUTH-ARCH-001 | truthOS與果蠅實驗本質對齊報告 | `docs/ISP-TRUTH-ARCH-001_truthOS與果蠅實驗本質對齊報告.md` | Architecture | Active | 戰略對齊：果蠅全腦仿真與 truthOS 精神映射。 |
| ISP-TRUTH-ARCH-002 | Platform Module Mapping | `docs/ISP-TRUTH-ARCH-002_Platform_Module_Mapping.md` | Architecture | Active | 模組映射：從 Connectome 到 Truth Graph。 |
| ISP-TRUTH-SPEC-001 | English Execution Prompt | `docs/ISP-TRUTH-SPEC-001_English_Execution_Prompt.md` | Specification | Active | truthOS 的 Agent 執行 Prompt 與約束。 |

---

## 4. 報表與營運記憶

以下內容通常不放在 `docs/`，但屬於文件系統的重要延伸：

- daily reports
- weekly summaries
- monthly summaries
- incident postmortems
- runbook manifest

建議視為「operational memory artifacts」，並由本索引統一指向其根目錄位置。

### 建議根目錄
- `~/.openclaw/reports/daily`
- `~/.openclaw/reports/weekly`
- `~/.openclaw/reports/monthly`
- `~/.openclaw/reports/incidents`
- `~/.openclaw/reports/runbook-manifest.*`

---

## 5. 文件分類規則

目前文件系統建議分為以下幾類：

- Architecture：架構總覽、分層說明、治理地圖
- Guide：開發、部署、節奏與操作導讀
- Runbook：故障、輪替、巡檢、恢復等可操作文件
- Policy：治理規則、命名規則、邊界規則
- Index：文件入口、總索引、導覽頁
- Report：closeout、acceptance、phase summary、週報、月報
- Incident：事故紀錄與 postmortem

---

## 6. 維護規則

每新增一份正式文件，應同步完成以下動作：

1. 分配檔案編號。
2. 寫入封面資訊。
3. 更新版本變更紀錄。
4. 加入本索引表。
5. 補上關聯檔案。

每次重大重構後，應檢查：
- 是否有文件已過時
- 是否需要標註 deprecated / superseded
- 是否有新分類需要加入

---

## 7. 文件狀態定義

- `Draft`：草稿中，內容未完成
- `Review`：待審閱
- `Active`：現行有效版本
- `Deprecated`：仍保留，但不建議繼續使用
- `Superseded`：已被新文件取代
- `Archived`：封存，不再更新

---

## 8. 文件系統原則

文件不是附件，而是系統記憶的一部分。

當架構變複雜時，
索引讓人找得到路；
編號讓文件有身份；
版本讓變化可被誠實記錄。
