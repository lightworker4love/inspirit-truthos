# Phase 1.5 / 2 RC 完成：Case Identity 全鏈路、Blueprint Writeback、Guarded Soul Insight 已就位

團隊各位、合作夥伴好，  
Phase 1.5 / 2 的 RC 收斂已完成，這一輪已進入可 review、可 merge、可發布的狀態。

## 這次完成了什麼

- `preferred_name` 全鏈路已打通：wisdom session -> frontend state -> chat metadata -> backend request model -> `CaseResolver` -> `PromptBuilder` -> `compose_response()`
- Hank 命名問題已從個別修補改為機制化保證（由優先序與測試共同守住）
- `CaseProfile.schema_version = 1` 已建立資料結構版本基線
- `update_case_blueprint_from_conversation()` 已上線 minimal writeback（僅 `last_session_insight`, `life_themes`, `blind_spots`）
- `infer_soul_age()` 已加 strict guard，資料不足不輸出結論
- blueprint writeback observability 已補齊，可追蹤觸發/跳過與原因，且不輸出敏感原文
- RC checklist、驗收報告、正式摘要文件已完備

## 為什麼這很重要

這次不是只修正一個名字，而是把平台底層從 session token 邏輯推進到 case identity 邏輯。  
同時，平台也從 chat memory 走向 case-care memory：在不過度推論的前提下，開始累積可持續的個案陪伴脈絡。  
這使我們能在下一階段有節奏地擴展 mem0/Qdrant、Blind Spot Profile 與 Life Blueprint，而不是在不穩定基礎上堆功能。

## 目前限制

- `soul_age` 目前定位為 `advisory / guarded / experimental`，不是 definitive truth
- blueprint extraction 目前仍是 minimal、rule-based
- 正式 release 前，仍需依 `release-candidate-checklist.md` 完成部署與 smoke 驗證

## 下一步

- merge cleanup（隔離 unrelated changes，確保 PR 邊界乾淨）
- observability extension（從事件日誌擴展到可持續追蹤）
- reviewed extraction / classifier（在 guardrail 與人工審視下推進）
- store / sync strengthening（JSON -> SQLite/Postgres 路徑與 mem0/Qdrant 對齊）

---

## Slack TL;DR（短版）

Phase 1.5 / 2 RC 已完成，交付已進入可 merge / 可發布狀態。  
這次不是只修一個名字，而是把平台從 session token 推進到 case identity。  
同時也從 chat memory 推進到 case-care memory，開始有節制地累積個案陪伴記憶。  
`preferred_name` 全鏈路、minimal blueprint writeback、guarded `soul_age` 已就位。  
`soul_age` 仍是 advisory/guarded/experimental，不是 definitive truth。  
下一步是 merge cleanup、observability extension、reviewed extraction、與 store/sync 強化。  
