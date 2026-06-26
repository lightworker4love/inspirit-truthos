# DOC-ID-RULES.md

# in spirit AI 文件編號規則

## 1. 目的

本文件定義 in spirit AI 平台於本機治理層、ops 系統、架構文件、runbooks 與階段性交付文件的統一編號規則。

目標是讓文件具備：
- 可辨識
- 可排序
- 可追蹤
- 可交接
- 可擴充

---

## 2. 基本格式

統一格式如下：

`[ORG]-[DOMAIN]-[TYPE]-[NNN]`

範例：

- `ISP-OPS-ARCH-001`
- `ISP-OPS-RUNBOOK-002`
- `ISP-TRUTH-SPEC-003`
- `ISP-OPS-INCIDENT-004`

---

## 3. 欄位定義

### 3.1 ORG
代表組織或平台識別碼。

目前固定使用：

- `ISP` = in spirit AI

### 3.2 DOMAIN
代表文件所屬領域。

建議值如下：

- `OPS` = operations / 維運 / 節奏 / runbooks
- `TRUTH` = truth-api / 本機治理層 / 個案治理
- `PLAT` = platform / OpenClaw / Gateway / control-plane
- `SEC` = security / secrets / auth / boundary
- `REL` = release / phase / rollout / handoff

### 3.3 TYPE
代表文件類型。

建議值如下：

- `ARCH` = architecture / 架構總覽
- `SPEC` = specification / 規格
- `GUIDE` = guide / 指南
- `RUNBOOK` = 操作手冊
- `INCIDENT` = 事故回顧 / postmortem
- `REPORT` = 報告 / 週報 / 月報 / closeout
- `INDEX` = 索引文件
- `POLICY` = 規範 / 政策
- `CHECKLIST` = 驗收或操作清單
- `ROADMAP` = 路線圖
- `BASELINE` = 凍結基準文件

### 3.4 NNN
三位數流水號，自 `001` 起算。

規則如下：
- 同一個 DOMAIN + TYPE 底下獨立編號。
- 流水號不回收。
- 已廢止文件也不重用舊號。

---

## 4. 命名原則

正式文件檔名建議採以下格式：

`[DOC-ID]_[中文文件名].md`

範例：

- `ISP-OPS-ARCH-001_本機治理層建設歷程總覽.md`
- `ISP-OPS-INDEX-001_docs文件總索引.md`
- `ISP-OPS-POLICY-001_檔案編號規則.md`
- `ISP-TRUTH-SPEC-001_個案身份閘門規格.md`

如需英文檔名，可改為：

`[DOC-ID]_[english-title].md`

---

## 5. 分類建議

### 5.1 治理與 ops 類
- `ISP-OPS-ARCH-*`
- `ISP-OPS-RUNBOOK-*`
- `ISP-OPS-REPORT-*`
- `ISP-OPS-INDEX-*`
- `ISP-OPS-POLICY-*`

### 5.2 truth-api / 個案治理類
- `ISP-TRUTH-ARCH-*`
- `ISP-TRUTH-SPEC-*`
- `ISP-TRUTH-POLICY-*`
- `ISP-TRUTH-GUIDE-*`

### 5.3 平台與 Gateway 類
- `ISP-PLAT-ARCH-*`
- `ISP-PLAT-SPEC-*`
- `ISP-PLAT-ROADMAP-*`

### 5.4 安全與邊界類
- `ISP-SEC-POLICY-*`
- `ISP-SEC-RUNBOOK-*`
- `ISP-SEC-INCIDENT-*`

### 5.5 release / 階段封板類
- `ISP-REL-REPORT-*`
- `ISP-REL-CHECKLIST-*`
- `ISP-REL-BASELINE-*`
- `ISP-REL-GUIDE-*`

---

## 6. 編號分配規則

1. 新文件建立前，先查 `docs/INDEX.md`。
2. 選定 DOMAIN 與 TYPE。
3. 取該分類下下一個未使用流水號。
4. 建立檔名、封面資訊與版本紀錄。
5. 將新文件加入 `docs/INDEX.md`。

---

## 7. 版本與文件編號的關係

- 文件編號識別「哪一份文件」。
- 版本號識別「這份文件更新到哪一版」。

範例：
- 文件編號：`ISP-OPS-ARCH-001`
- 版本號：`v1.2`

這代表同一份文件已更新到第 1.2 版，但文件身份仍然不變。

---

## 8. 廢止與取代規則

若文件被取代：

- 原文件保留原編號。
- 文件狀態改為 `Superseded` 或 `Deprecated`。
- 新文件取得新編號。
- 在 `docs/INDEX.md` 中標註「取代關係」。

不得以新內容覆蓋舊編號的歷史文件身份。

---

## 9. 最小必備欄位

所有正式文件至少應包含：

- 檔案編號
- 文件名稱
- 版本號
- 文件狀態
- 建立日期
- 最後更新日期
- 作者
- 文件目的
- 適用範圍
- 版本變更紀錄
- 關聯檔案

---

## 10. 原則

好的文件編號不是官僚化，而是讓系統在時間裡仍能被辨識。

當檔案數量變多時，
編號是秩序；
索引是記憶；
版本是誠實。
