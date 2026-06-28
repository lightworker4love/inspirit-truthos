# docs/CHANGELOG.md

# in spirit AI Documentation & Governance Changelog

- 檔案編號：ISP-OPS-REPORT-001
- 文件名稱：Documentation & Governance Changelog
- 文件類型：Report
- 文件狀態：Active
- 版本號：v1.0
- 建立日期：2026-03-16
- 最後更新：2026-03-16
- 作者：Light Worker / in spirit AI

---

## 1. 目的

本文件用於記錄 in spirit AI 本機治理層相關文件系統、ops 制度與治理結構的演進歷程。

本文件聚焦於：
- 文件新增
- 文件升級
- 制度建立
- 文件關係調整
- 治理節奏成形

本文件不取代 Git commit log，也不取代 incident postmortem。

---

## 2. 使用原則

每當發生以下情況時，應更新本文件：

- 新增正式文件
- 重要文件升級版本
- 文件命名與分類規則調整
- 文件索引架構調整
- ops 節奏、runbook 制度或治理邊界發生顯著變化

---

## 3. 變更紀錄

## 2026-03-16

### Added
- 建立本機治理層建設歷程總覽文件，作為治理敘事總覽。
- 建立檔案編號規則，統一正式文件命名與分類。
- 建立 `docs/INDEX.md`，作為文件系統導航入口。
- 建立 `docs/CHANGELOG.md`，作為制度與文件演進時間軸。
- 建立 `docs/DECISIONS.md`，作為關鍵架構決策紀錄。
- 建立 `ISP-TRUTH-ARCH-001_truthOS與果蠅實驗本質對齊報告.md`，對齊戰略命題。
- 建立 `ISP-TRUTH-ARCH-002_Platform_Module_Mapping.md`，落實技術與模組映射。
- 建立 `ISP-TRUTH-SPEC-001_English_Execution_Prompt.md`，定義 LLM / Agent 執行指令。

### Expanded
- 將單一 ops 文件逐步擴展為 daily / weekly / monthly / incident 的節奏化記憶系統。
- 將 runbooks、ops architecture、status panel、runbook manifest 收束到同一個治理文檔脈絡中。

### Standardized
- 定義正式文件最小必備欄位，包括檔案編號、版本號、作者、適用範圍、版本紀錄與關聯檔案。
- 建立文件狀態語義，包括 Draft、Review、Active、Deprecated、Superseded、Archived。

### Notes
- 本次更新標誌文件系統從單篇成熟，進入整體有序階段。
- 後續應以 INDEX、CHANGELOG、DECISIONS 三者共同維護文件秩序。

---

## 4. 建議紀錄格式

未來新增 changelog 項目時，建議使用以下結構：

## YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Expanded
- ...

### Deprecated
- ...

### Notes
- ...

---

## 5. 文件狀態說明

- `Added`：首次建立的新文件或新制度
- `Changed`：既有文件重大改版
- `Expanded`：既有制度或結構範圍擴大
- `Standardized`：命名、編號、格式或流程被正式定義
- `Deprecated`：不再建議使用，但保留歷史參考價值
- `Notes`：補充背景、影響範圍與下一步提醒

---

## 6. 原則

Changelog 記錄的不是熱鬧，而是秩序如何形成。

當時間過去之後，
它幫助團隊記得：
- 什麼時候開始有規則
- 什麼時候開始有節奏
- 什麼時候開始把知識變成制度
