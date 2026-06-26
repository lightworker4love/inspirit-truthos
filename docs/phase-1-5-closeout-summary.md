# Phase 1.5 / 2 Closeout Summary

## 本輪目標

本輪聚焦於把 case identity 與最小 case-memory 能力從可用狀態推進到可驗收、可發布狀態，並完成 RC 驗證與正式交付文件。

## 本輪相關檔案盤點

### Core Code

- `apps/truth-api/app/main.py`
- `apps/truth-api/app/models.py`
- `apps/truth-api/app/case_models.py`
- `apps/truth-api/app/case_resolver.py`
- `apps/truth-api/app/prompt_builder.py`
- `apps/truth-api/app/case_insight_service.py`
- `apps/truth-api/app/reasoning.py`

### Tests

- `apps/truth-api/tests/test_case_identity_phase_1_5.py`
- `../upstream/openclaw/ui/src/ui/app-lifecycle.node.test.ts`
- `../upstream/openclaw/ui/src/ui/controllers/chat.test.ts`

### Docs

- `docs/case-identity-sequence.md`
- `docs/case-profile-schema.md`
- `docs/release-candidate-checklist.md`
- `docs/phase-1-acceptance-report.md`
- `docs/phase-1-formal-summary.md`
- `docs/phase-1-exec-summary.md`
- `docs/phase-2-technical-roadmap.md`
- `docs/phase-1-5-closeout-summary.md` (this file)

### Scripts / Validation

- `scripts/rc_validate_phase_1_5.sh`

## 已完成項目

- `preferred_name` 全鏈路打通（wisdom session -> frontend state -> chat metadata -> backend -> resolver -> prompt -> response）
- `CaseProfile.schema_version = 1`
- `update_case_blueprint_from_conversation()` 僅更新：
  - `last_session_insight`
  - `life_themes`
  - `blind_spots`
- `infer_soul_age()` 已加 strict eligibility guard，資料不足不輸出結論
- blueprint writeback observability 已補上（無 raw transcript dump）
- RC checklist 與可重複執行 script 已建立，並完成一次通過驗證

## 主要技術成果

1. Identity continuity 正式機制化，`preferred_name` 優先序在 API 與 resolver 層明確落地。
2. Minimal blueprint writeback 具備低風險持久化與 identity-preserving 行為。
3. `soul_age` 已被限制為 `advisory + guarded + experimental + non-definitive`，避免對外過度敘事。
4. writeback decision 已可觀測（`case_id`, `triggered/skipped`, `updated_fields`, `skip_reason`, `soul_age_guard`）。
5. 文件集合完整，可支援對內 review、對外里程碑同步、與 RC 執行交接。

## 驗收與測試結果

- `python -m py_compile`（核心後端檔案）通過
- `pytest apps/truth-api/tests/test_case_identity_phase_1_5.py -q` 通過
- `bash scripts/rc_validate_phase_1_5.sh` 通過，包含：
  - backend syntax/tests
  - openclaw UI build
  - openclaw gateway/runtime build
  - Hank/fallback/writeback/soul guard smoke checks

## 剩餘風險

- `soul_age` 仍為 early-stage inference，雖已 guarded，但不應作為 external truth claim。
- blueprint extraction 目前是 minimal rule-based，尚未進入 reviewed classifier/prompt extraction 流程。
- 工作樹目前有大量 unrelated changes；若不隔離，容易污染本票變更邊界。
- 測試中有 Pydantic deprecation warnings（不阻擋 RC，但建議排入下一輪清理）。

## 建議下一步

1. 先做變更隔離，產生純淨 Phase 1.5 / 2 提交集。
2. 依 review 優先順序完成 code review 與 docs sign-off。
3. 按 RC checklist 在 staging 再執行一次，保留驗證紀錄。
4. 完成 merge 後發布 Slack/Notion milestone update，並啟動 Phase 2 hardening。

## 建議 Merge / Release 順序

1. 核心程式碼（identity + blueprint + guard）  
   `case_models.py`, `case_resolver.py`, `prompt_builder.py`, `case_insight_service.py`, `main.py`, `models.py`
2. 測試  
   `test_case_identity_phase_1_5.py` + openclaw UI related tests
3. RC script / checklist  
   `scripts/rc_validate_phase_1_5.sh`, `docs/release-candidate-checklist.md`
4. 正式報告與對外摘要  
   `phase-1-acceptance-report.md`, `phase-1-formal-summary.md`, `phase-1-exec-summary.md`, `phase-1-slack-announcement.md`

## Recommended merge order
1. core-identity-and-blueprint
2. rc-validation-and-checklist
3. formal-docs-and-announcement

## Merge / Release 建議（Review 分流）

- 優先 review 檔案（blocking）：
  - `apps/truth-api/app/case_insight_service.py`
  - `apps/truth-api/app/case_models.py`
  - `apps/truth-api/app/main.py`
  - `apps/truth-api/tests/test_case_identity_phase_1_5.py`
  - `scripts/rc_validate_phase_1_5.sh`
- Supporting docs（non-blocking but required for release communication）：
  - `docs/release-candidate-checklist.md`
  - `docs/phase-1-acceptance-report.md`
  - `docs/phase-1-formal-summary.md`
  - `docs/phase-1-exec-summary.md`
  - `docs/case-profile-schema.md`
  - `docs/phase-2-technical-roadmap.md`
  - `docs/phase-1-5-closeout-summary.md`
  - `docs/phase-1-slack-announcement.md`
- Release scripts：
  - `scripts/rc_validate_phase_1_5.sh`

## Commit / PR 切分建議

建議至少拆成 3 個 PR（避免超大單一 PR）：

1. `core-identity-and-blueprint`  
   core code + tests（不含大量文檔）
2. `rc-validation-and-checklist`  
   `rc_validate_phase_1_5.sh` + `release-candidate-checklist.md`
3. `formal-docs-and-announcement`  
   acceptance/formal/exec/closeout/slack docs

## Unrelated Changes 隔離建議

目前 `inspirit-truthos` 與 `upstream/openclaw` 都有大量非本票變更。為避免混入：

- 使用 path-based staging（只 `git add` 本票檔案清單）
- 每個 PR 前以 `git diff --name-only` 對照本文件的「本輪相關檔案盤點」
- 不在同一 PR 夾帶 UI 視覺、locale、layout 或其他非 case identity 變更
- 若需要，先以新分支 cherry-pick 乾淨 commit，再提 PR
