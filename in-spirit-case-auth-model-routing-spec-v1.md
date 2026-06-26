# in spirit 個案身份驗證與模型路由規格 v1

## 1. 目的與邊界

### 1.1 目標

本規格定義 in spirit AI 智慧平台在**本機環境**中的個案身份驗證、角色授權、模型白名單切換、對話記錄與審計機制。  
第一版目標不是建立通用聊天站，而是建立一個**受治理的個案入口層**，讓不同身份的人只進入自己被允許的對話空間。

### 1.2 平台精神

本系統必須對齊 in spirit 的核心精神：

- 安全先於自由。
- 引導先於暴露。
- 身份清晰先於功能堆疊。
- 模型是承載，不是主角。
- 個案進入的是被照看的容器，不是直接接觸底層機房。

### 1.3 現況假設

目前平台的既有技術基底如下：

- OpenClaw Gateway 運行於本機，主線錨定在 `127.0.0.1:18789`。
- `~/.openclaw/openclaw.json` 是 OpenClaw 的單一設定來源，包含 models、agents 與 gateway auth 等配置。
- `inspirit-truthos` 已存在，truth API 入口位於 `apps/truth-api/app/main.py`。
- `secondme-proxy` 已存在，為 Node/Express 中介層。
- `custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit` 已是現有本機 custom provider 主路由的一部分。
- `memory-lancedb-pro` 的 stale references 已自 config 中移除，以避免舊插件復活影響 Gateway 穩定性。

### 1.4 不在 v1 範圍內

以下項目不納入 v1：

- 對外公開註冊。
- 多租戶 SaaS 架構。
- 個案直接進入 OpenClaw Control UI。
- 自動長期記憶回寫到向量資料庫。
- trusted-proxy SSO / OAuth 完整整合。
- 財務、付款、訂閱管理。

***

## 2. 角色、模型與系統架構

### 2.1 角色定義

系統定義兩種核心角色：

#### A. `case_client`
用途：
- 靈性對話
- 生命練習
- 溫和反思
- 日常陪伴式對話

可用模型：
- `gemini-bible/gemini-2.5-flash`
- `custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit`

限制：
- 不可切換到開發模型
- 不可檢視系統 prompt
- 不可修改模型政策
- 不可直接接觸 OpenClaw Gateway 原始設定
- 不可直接進入 OpenClaw Control UI

#### B. `admin_builder`
用途：
- 開發
- prompt 建構
- workflow 設計
- 模型策略調校
- 審計與維運

可用模型：
- `openai-responses/gpt-5.4`
- `custom-127-0-0-1-8000/gpt-5.3-codex`

限制：
- 必須具有更高等級驗證
- 所有 prompt 變更與模型切換需留審計紀錄

### 2.2 UI 顯示原則

前端不直接向個案顯示底層模型 ID。  
個案端應顯示為平台語意模式，例如：

- `靜心陪伴模式` → `custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit`
- `經文映照模式` → `gemini-bible/gemini-2.5-flash`

管理者端才顯示技術模型 ID。

### 2.3 模型決策原則

前端可提出「模式選擇」，但**後端才是最終模型裁決者**。  
也就是說：

- 前端送出 `mode=spiritual_reflection` 或 `mode=builder_workbench`
- 後端根據 `role + policy + availability` 解析最終模型
- OpenClaw / provider 只接收後端已核准的模型路由結果

### 2.4 系統架構

建議架構如下：

```text
[ Case Client UI / Admin UI ]
            │
            ▼
[ inSpirit Auth + Policy API ]
  - login/logout
  - RBAC
  - model allowlist
  - audit logging
  - thread storage
            │
            ▼
[ truth-api / secondme-proxy adapter layer ]
            │
            ▼
[ OpenClaw Gateway @ 127.0.0.1:18789 ]
            │
   ┌────────┴────────┐
   ▼                 ▼
[oMLX local]     [Cloud providers]
Qwen3.5-9B       GPT-5.4 / Gemini
```

### 2.5 核心原則

1. 個案不得直接呼叫 OpenClaw Gateway。  
2. 所有對話必須經過平台 API。  
3. 身份、權限、模型政策、審計必須在平台 API 層完成。  
4. OpenClaw 是 orchestration layer，不是個案入口層。
5. oMLX 是本機推理層，OpenAI/Gemini 等屬外部能力層，不應讓個案直接操作 provider 細節。

***

## 3. 資料模型與儲存規格

### 3.1 儲存策略

v1 採用：

- **SQLite**：身份、權限、thread、審計、會話索引。
- **Markdown / Obsidian 匯出層**：個案摘要、回顧、練習紀錄。
- **未來保留**：LanceDB / 長期記憶回寫。

這與既有平台偏好一致，因為你已經在 OpenClaw 生態中建立主題式記憶與檔案層 / 向量層分工經驗。

### 3.2 SQLite 資料表

#### `users`
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('case_client', 'admin_builder')),
  status TEXT NOT NULL DEFAULT 'active',
  totp_secret TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_login_at TEXT
);
```

#### `case_profiles`
```sql
CREATE TABLE case_profiles (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  legal_name TEXT,
  intake_status TEXT NOT NULL DEFAULT 'pending',
  consent_version TEXT,
  assigned_admin_id TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### `auth_sessions`
```sql
CREATE TABLE auth_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  device_id TEXT,
  ip_address TEXT,
  user_agent TEXT,
  issued_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### `model_policies`
```sql
CREATE TABLE model_policies (
  id TEXT PRIMARY KEY,
  role TEXT NOT NULL,
  mode_key TEXT NOT NULL,
  model_id TEXT NOT NULL,
  is_default INTEGER NOT NULL DEFAULT 0,
  enabled INTEGER NOT NULL DEFAULT 1,
  purpose TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

#### `case_threads`
```sql
CREATE TABLE case_threads (
  id TEXT PRIMARY KEY,
  case_user_id TEXT NOT NULL,
  created_by_user_id TEXT NOT NULL,
  selected_mode_key TEXT NOT NULL,
  resolved_model_id TEXT NOT NULL,
  thread_type TEXT NOT NULL DEFAULT 'dialogue',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (case_user_id) REFERENCES users(id),
  FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);
```

#### `case_entries`
```sql
CREATE TABLE case_entries (
  id TEXT PRIMARY KEY,
  thread_id TEXT NOT NULL,
  speaker TEXT NOT NULL CHECK (speaker IN ('user', 'assistant', 'system', 'admin_note')),
  content TEXT NOT NULL,
  content_type TEXT NOT NULL DEFAULT 'text',
  exercise_type TEXT,
  tags TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (thread_id) REFERENCES case_threads(id)
);
```

#### `audit_logs`
```sql
CREATE TABLE audit_logs (
  id TEXT PRIMARY KEY,
  actor_user_id TEXT,
  action TEXT NOT NULL,
  target_type TEXT,
  target_id TEXT,
  resolved_model_id TEXT,
  result TEXT NOT NULL,
  metadata_json TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (actor_user_id) REFERENCES users(id)
);
```

#### `prompt_versions`
```sql
CREATE TABLE prompt_versions (
  id TEXT PRIMARY KEY,
  audience TEXT NOT NULL CHECK (audience IN ('case_client', 'admin_builder')),
  version TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  content_body TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 0,
  created_by_user_id TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);
```

### 3.3 種子資料

v1 應內建最少 seed：

- 1 位 `case_client`
- 1 位 `admin_builder`
- 4 筆模型政策
- 2 組 mode labels（個案端）
- 1 組 admin builder 預設模型政策

***

## 4. API、授權與安全規格

### 4.1 認證方式

#### case_client
- username + password
- 可選邀請碼 / 啟用碼
- session cookie 或 signed bearer session token

#### admin_builder
- username + password
- 預留 TOTP 欄位
- v1 可先啟用 TOTP placeholder，v2 強制開啟

密碼雜湊必須採用：
- **Argon2id** 優先
- 若技術受限則退回 bcrypt

### 4.2 API 端點

#### `POST /auth/login`
輸入：
```json
{
  "username": "hank",
  "password": "********"
}
```

輸出：
```json
{
  "user": {
    "id": "usr_xxx",
    "role": "case_client",
    "displayName": "Hank"
  },
  "session": {
    "token": "session_xxx",
    "expiresAt": "2026-03-17T00:00:00Z"
  }
}
```

#### `POST /auth/logout`
- 使目前 session 失效
- 寫入 audit log

#### `GET /me`
- 回傳目前身份
- 回傳 role
- 回傳可見 UI capabilities

#### `GET /models/allowed`
回傳目前角色可見模式，而非原始 provider 全清單。

個案端示例：
```json
{
  "modes": [
    {
      "key": "spiritual_reflection",
      "label": "靜心陪伴模式",
      "default": true
    },
    {
      "key": "scripture_reflection",
      "label": "經文映照模式",
      "default": false
    }
  ]
}
```

#### `POST /threads`
建立新 thread：

```json
{
  "mode": "spiritual_reflection"
}
```

#### `POST /chat`
前端送：

```json
{
  "threadId": "thr_xxx",
  "message": "我最近很焦慮，不知道怎麼安定下來。",
  "mode": "spiritual_reflection"
}
```

後端行為：
1. 驗證 session
2. 驗證 role
3. 驗證 mode 是否屬白名單
4. 解析最終模型 ID
5. 寫入 audit
6. 呼叫 OpenClaw / provider
7. 寫回對話紀錄

#### `GET /threads/:id`
回傳 thread 與 entries

#### `GET /admin/audit`
僅 `admin_builder` 可見

### 4.3 OpenClaw Adapter 規格

平台後端送往 OpenClaw / OpenAI-compatible payload 時：

- 不得把 `display_name`
- 不得把 `login_username`
- 不得把任何 UI-only 身份欄位塞進 raw payload root

前端身份欄位應只存在平台層，不直接注入底層 `chat.send` 結構。  
這是為了避免再次發生 schema mismatch 類錯誤，也讓平台邊界保持乾淨。

### 4.4 模型解析規則

#### case_client
```text
if mode == spiritual_reflection:
  resolve -> custom-127-0-0-1-8000/Qwen3.5-9B-MLX-4bit

if mode == scripture_reflection:
  resolve -> gemini-bible/gemini-2.5-flash
```

#### admin_builder
```text
if mode == builder_workbench:
  resolve -> custom-127-0-0-1-8000/gpt-5.3-codex

if mode == deep_admin_analysis:
  resolve -> openai-responses/gpt-5.4
```

### 4.5 安全控制

- case_client 不可直連 OpenClaw Gateway
- 不暴露 Gateway token 給個案端
- 管理者與個案 session 分離
- 所有模型選擇事件寫入 `audit_logs`
- 所有 prompt 變更寫入 `prompt_versions`
- 所有管理者行為需可審計
- 敏感欄位不得明文回傳前端
- v1 不啟用自動記憶回寫，避免個案內容被過早固化

***

## 5. 實作階段、驗收與運維

### 5.1 Phase 1：最小可用版

交付內容：

- SQLite schema
- Auth API
- RBAC
- Model policy enforcement
- Thread / entry storage
- Audit logs
- Basic admin UI / case UI
- OpenClaw adapter layer

成功標準：

- 個案能登入
- 個案只能看見 2 個靈性模式
- 管理者只能看見 2 個管理模式
- 後端能正確解析成目標模型
- thread / audit 均可落地
- 個案端完全不暴露 Gateway token 或 raw provider config

### 5.2 Phase 2：記錄與引導升級

交付內容：

- 會談摘要
- 練習卡片
- Markdown / Obsidian 匯出
- 管理者 review queue
- 事件標籤與主題分類

### 5.3 Phase 3：治理深化

交付內容：

- prompt 版本控管
- admin prompt compare
- memory writeback approval flow
- 使用量 / 成本 / 延遲監控
- 個案安全警示規則

### 5.4 Operator 檢查清單

每日檢查：

- SQLite 檔案可讀寫
- OpenClaw Gateway 健康
- 本機 oMLX provider 健康
- admin login 正常
- case login 正常
- audit log 正常寫入

升級後檢查：

- `openclaw.json` 未被外部工具覆寫
- local custom provider 仍可用
- 個案白名單模型未漂移
- admin 白名單模型未漂移
- Gateway schema 未破壞 adapter

### 5.5 驗收標準

本規格完成的驗收條件如下：

- 至少 1 位個案可登入並完成對話
- 至少 1 位管理者可登入並進行 prompt 建構對話
- case_client 無法越權切到 admin 模型
- admin_builder 可見審計記錄
- 平台層能清楚記錄「誰在什麼時間使用哪個模型」
- 對話入口、模型白名單、審計邊界彼此分離
- 未直接暴露 OpenClaw Gateway 給個案端

### 5.6 最終原則

這套系統不是為了讓更多人自由切模型，  
而是為了讓每個人只進入自己被允許、被祝福、被看顧的那個對話空間。
