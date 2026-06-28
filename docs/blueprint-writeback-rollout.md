# Blueprint Writeback 本機開關與回退

## 目的

這份文件只描述 `BLUEPRINT_WRITEBACK_ENABLED` 在本機 TruthOS 安裝中的控制方式。

本輪原則：
- Query 主路徑必須可用
- writeback 必須可開可關
- 關閉時不得進入 writeback load path
- 不修改 OpenClaw 主線設定
- 不把 Antigravity 當成主鏈路

## 正式開關入口

目前正式入口如下：
- `/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api/app/config.py`
- `/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api/app/main.py`
- `/Users/tongwei/.openclaw/inspirit-truthos/docker-compose.yml`
- `/Users/tongwei/.openclaw/inspirit-truthos/.env.example`
- `/Users/tongwei/.openclaw/inspirit-truthos/env/truthos.dev.env`
- `/Users/tongwei/.openclaw/inspirit-truthos/env/truthos.staging.env`
- `/Users/tongwei/.openclaw/inspirit-truthos/env/truthos.prod.env`

預設值：

```env
BLUEPRINT_WRITEBACK_ENABLED=true
```

解析規則：
- `true / 1 / yes / on` -> 啟用
- 其他值或明確 `false / 0 / no / off` -> 關閉

## 關閉 writeback

### 一次性安全停用

不改 `.env`，直接用 shell override 重建 `truth-api`：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
BLUEPRINT_WRITEBACK_ENABLED=false docker compose up -d --force-recreate truth-api
```

### 驗證 off 狀態

```bash
curl -s http://127.0.0.1:18000/healthz | python3 -m json.tool
```

期待：
- `blueprint_writeback_enabled = false`

送一筆 query：

```bash
curl -s -X POST http://127.0.0.1:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank-login",
    "session_id": "rollout-off-001",
    "message": "I tried to help someone but it turned into conflict.",
    "preferred_name": "Hank",
    "login_username": "hank-login",
    "display_name": "Case Hank",
    "source_channel": "web"
  }' | python3 -m json.tool
```

檢查 log：

```bash
docker compose logs truth-api --since=2m | grep 'blueprint_event='
```

期待：
- query 仍回 200
- log 含 `blueprint_event=blueprint_writeback_disabled`
- 不應因 writeback 關閉而影響主 query response

## 啟用 writeback

### 一次性重新啟用

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
BLUEPRINT_WRITEBACK_ENABLED=true docker compose up -d --force-recreate truth-api
```

### 驗證 on 狀態

```bash
curl -s http://127.0.0.1:18000/healthz | python3 -m json.tool
```

期待：
- `blueprint_writeback_enabled = true`

送同一筆 query 後檢查 log：

```bash
docker compose logs truth-api --since=2m | grep 'blueprint_event='
```

期待：
- query 仍回 200
- log 可見 `blueprint_update_considered` 或後續 gated event
- 不要求每次都實際寫入，但流程必須能進 gate 判斷

## CaseResolver 驗證

使用 Hank 類型案例：

```bash
curl -s -X POST http://127.0.0.1:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank-login",
    "session_id": "case-resolver-001",
    "message": "I keep over-explaining and feel pressure at work.",
    "preferred_name": "Hank",
    "login_username": "hank-login",
    "display_name": "Case Hank",
    "source_channel": "web"
  }' | python3 -m json.tool
```

期待：
- `case_id` 類似 `case:web:hank-login`
- `mirror` 以 `Hank，` 開頭
- `preferred_name / login_username` 鏈路未被破壞

## 安全回退

### 最小回退

如果本輪安裝後只想停用 writeback，不拆服務：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
BLUEPRINT_WRITEBACK_ENABLED=false docker compose up -d --force-recreate truth-api
```

### 回到安裝前保守狀態

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose stop truth-api
```

如果先前服務已在跑，也可直接回到既有 `.env` 設定再重建：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose up -d --force-recreate truth-api
```

本輪沒有修改：
- `~/.openclaw/openclaw.json`
- OpenClaw 主線 gateway 設定
- Antigravity 整合狀態
